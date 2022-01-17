import asyncio
import inspect
import typing
from traitlets import Integer, TraitError, validate, Bool, Callable
from traitlets.config import SingletonConfigurable
from asyncio import Queue


class GraderExecutor(SingletonConfigurable):
    n_concurrent_tasks = Integer(default_value=5, allow_none=False).tag(config=True)
    resubmit_cancelled_tasks = Bool(default_value=False, allow_none=False).tag(config=True)
    get_event_loop = Callable(default_value=asyncio.get_event_loop, allow_none=False).tag(config=True)

    async def task_executor(self):
        coro, on_finish = (None, None)
        try:
            while self.running:
                coro, on_finish = await self.queue.get()
                await coro()
                if on_finish is not None:
                    if inspect.iscoroutinefunction(on_finish):
                        await on_finish()
                    else:
                        on_finish()
                self.queue.task_done()
        except asyncio.CancelledError:
            if self.resubmit_cancelled_tasks and coro is not None:
                self.queue.put_nowait((coro, on_finish))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.running = True
        self.queue = Queue()
        self.loop = self.get_event_loop()
        self.workers = [self.loop.create_task(self.task_executor()) for _ in range(self.n_concurrent_tasks)]

    def submit(self, task: typing.Callable, on_finish: typing.Callable = None):
        """
        Submit a task to be processed by the executor.

        :param task: The task to be executed.
        :param on_finish: Callable that is executed when submitted task finishes.
            Can be synchronous or asynchronous call.
        """
        self.queue.put_nowait((task, on_finish))

    def cancel_tasks(self):
        """
        Immediately cancel all tasks being executed.
        """
        for worker in self.workers:
            worker.cancel()
        self.running = False

    async def stop(self, timeout=5):
        """
        Wait for tasks to finish within the timout and cancel remaining tasks.

        :param timeout: Timeout in seconds.
        """
        self.running = False
        done, pending = await asyncio.wait(self.workers, timeout=timeout)
        for fut in pending:
            fut.cancel()
        self.workers = None

    def start(self):
        """
        Restart the executor. If it is already running this has no effect.
        """
        if self.running:
            return
        self.running = True
        self.workers = [self.loop.create_task(self.task_executor()) for _ in range(self.n_concurrent_tasks)]

    def remove_queued_tasks(self):
        """
        Remove all items in the queue.
        """
        self.queue = Queue()

    @validate("n_concurrent_tasks")
    def _validate_n_tasks(self, proposal):
        n = proposal.value
        if n <= 0:
            raise TraitError(f"Number of concurrent tasks has to be larger than 0, got: {n}")
        return n


if __name__ == "__main__":
    async def main():
        from random import randint

        def demo_task(code):
            async def wait_task():
                wait_time = randint(1, 3)
                print('running {} will take {} second(s)'.format(code, wait_time))
                await asyncio.sleep(wait_time)  # I/O, context will switch to main function
                print('ran {}'.format(code))

            return wait_task

        GraderExecutor.n_concurrent_tasks = 3
        GraderExecutor.resubmit_cancelled_tasks = True
        executor = GraderExecutor.instance()
        for i in range(9):
            task = demo_task(i)

            async def p():
                await asyncio.sleep(0.5)
                print(f"Queue Size: {executor.queue.qsize()}")
            executor.submit(task, p)
        await asyncio.sleep(4)
        print("CANCEL")
        executor.cancel_tasks()
        print(executor.queue.qsize())
        executor.start()

        await asyncio.sleep(10)

    # need running asyncio loop
    asyncio.run(main())