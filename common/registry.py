
from typing import List, Set, Tuple
from tornado.web import RequestHandler
from jupyter_server.utils import url_path_join


class Singleton(type):
  _instances = {}

  def __call__(cls, *args, **kwargs):
      if cls not in cls._instances:
          cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
      return cls._instances[cls]


class HandlerPathRegistry(object, metaclass=Singleton):
  registry = {}

  @property
  @staticmethod
  def path_set() -> Set[str]:
    return set(HandlerPathRegistry.registry.values())

  @property
  @staticmethod
  def path_list() -> List[str]:
    return list(HandlerPathRegistry.registry.values())

  @staticmethod
  def handler_list(base_url="api") -> List[Tuple[str, RequestHandler]]:
    return list(zip(
      [r"\/" + base_url + r"\/grader" + path for path in HandlerPathRegistry.registry.values()], 
      HandlerPathRegistry.registry.keys()
    ))

  @staticmethod
  def has_path(cls) -> bool:
    return cls in HandlerPathRegistry.registry

  @staticmethod
  def get_path(cls):
    return HandlerPathRegistry.registry[cls]

  @staticmethod
  def add(cls, path: str):
    # check if class inherits from tornado RequestHandler
    if RequestHandler not in cls.__mro__:
        raise ValueError(
            "Incorrect base class. Class has to be extended from tornado 'RequestHandler' in order to be registered."
        )
    HandlerPathRegistry.registry[cls] = path


def register_handler(path: str):
  def _register_class(cls):
    HandlerPathRegistry().add(cls, path)
    return cls
  return _register_class
