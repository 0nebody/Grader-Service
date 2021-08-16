import os
import glob
import re
import shutil
import sqlalchemy
import traceback
import importlib

from rapidfuzz import fuzz
from traitlets.config import LoggingConfigurable, Config
from traitlets import Bool, List, Dict, Integer, Instance, Type, Any, TraitError
from traitlets import default, validate
from textwrap import dedent
from nbconvert.exporters import Exporter, NotebookExporter
from nbconvert.writers import FilesWriter

# TODO: replace CourseDirectory with a path that can be supplied as an argument
# from ..coursedir import CourseDirectory
from utils import find_all_files, rmtree, remove
from preprocessors.execute import UnresponsiveKernelError
from nbgraderformat import SchemaTooOldError, SchemaTooNewError
import typing
from nbconvert.exporters.exporter import ResourcesDict


class GraderConvertException(Exception):
    pass


class BaseConverter(LoggingConfigurable):

    notebooks = List([])
    assignments = Dict({})
    writer = Instance(FilesWriter)
    exporter = Instance(Exporter)
    exporter_class = Type(NotebookExporter, klass=Exporter).tag(config=True)
    preprocessors = List([])

    force = Bool(False, help="Whether to overwrite existing files").tag(config=True)

    ignore = List(
        [
            ".ipynb_checkpoints",
            "*.pyc",
            "__pycache__",
            "feedback",
        ],
        help=dedent(
            """
            List of file names or file globs.
            Upon copying directories recursively, matching files and
            directories will be ignored with a debug message.
            """
        )
    ).tag(config=True)

    pre_convert_hook = Any(
        None,
        config=True,
        allow_none=True,
        help=dedent("""
        An optional hook function that you can implement to do some
        bootstrapping work before converting. 
        This function is called before the notebooks are converted
        and should be used for specific converters such as Autograde,
        GenerateAssignment or GenerateFeedback.

        It will be called as (all arguments are passed as keywords)::

            hook(assignment=assignment, student=student, notebooks=notebooks)
        """)
    )

    post_convert_hook = Any(
        None,
        config=True,
        allow_none=True,
        help=dedent("""
        An optional hook function that you can implement to do some
        work after converting. 
        This function is called after the notebooks are converted
        and should be used for specific converters such as Autograde,
        GenerateAssignment or GenerateFeedback.

        It will be called as (all arguments are passed as keywords)::

            hook(assignment=assignment, student=student, notebooks=notebooks)
        """)
    )

    permissions = Integer(
        help=dedent(
            """
            Permissions to set on files output by nbgrader. The default is
            generally read-only (444), with the exception of nbgrader
            generate_assignment and nbgrader generate_feedback, in which case
            the user also has write permission.
            """
        )
    ).tag(config=True)

    @default("permissions")
    def _permissions_default(self) -> int:
        return 664 if self.coursedir.groupshared else 444

    @validate('pre_convert_hook')
    def _validate_pre_convert_hook(self, proposal):
        value = proposal['value']
        if isinstance(value, str):
            module, function = value.rsplit('.', 1)
            value = getattr(importlib.import_module(module), function)
        if not callable(value):
            raise TraitError("pre_convert_hook must be callable")
        return value

    @validate('post_convert_hook')
    def _validate_post_convert_hook(self, proposal):
        value = proposal['value']
        if isinstance(value, str):
            module, function = value.rsplit('.', 1)
            value = getattr(importlib.import_module(module), function)
        if not callable(value):
            raise TraitError("post_convert_hook must be callable")
        return value

    # TODO: all file handling should happen here (no need for CourseDir) -> exporters have from_filename method
    def __init__(self, input_dir: str, output_dir: str, file_pattern: str, **kwargs: typing.Any) -> None:
        super(BaseConverter, self).__init__(**kwargs)
        self._input_directory = os.path.normpath(os.path.expanduser(input_dir))
        self._output_directory = os.path.normpath(os.path.expanduser(output_dir))
        self._file_pattern = file_pattern
        if self.parent and hasattr(self.parent, "logfile"):
            self.logfile = self.parent.logfile
        else:
            self.logfile = None

        c = Config()
        c.Exporter.default_preprocessors = []
        self.update_config(c)

    # register pre-processors to self.exporter
    # self.convert_notebooks() converts all notebooks in the CourseDir
    # notebooks are set in init_notebooks()
    def start(self) -> None:
        self.init_notebooks()
        self.writer = FilesWriter(parent=self, config=self.config)
        self.exporter = self.exporter_class(parent=self, config=self.config)
        for pp in self.preprocessors:
            self.exporter.register_preprocessor(pp)
        currdir = os.getcwd()
        os.chdir(self._output_directory)
        try:
            self.convert_notebooks()
        finally:
            os.chdir(currdir)

    @default("classes")
    def _classes_default(self):
        classes = super(BaseConverter, self)._classes_default()
        classes.append(FilesWriter)
        classes.append(Exporter)
        for pp in self.preprocessors:
            if len(pp.class_traits(config=True)) > 0:
                classes.append(pp)
        return classes


    # these methods rely on coursedir which should be replaced by configured functions
    # should return string that can be used for globs
    def _format_source(self, escape: bool = False) -> str:
        source = os.path.join(self._input_directory, self._file_pattern)
        if escape:
            return re.escape(source)
        else:
            return source


    def init_notebooks(self) -> None:
        self.notebooks = []
        notebook_glob = self._format_source()
        self.notebooks = glob.glob(notebook_glob)
        if len(self.notebooks) == 0:
            self.log.warning("No notebooks were matched by '%s'", notebook_glob)

    def init_single_notebook_resources(self, notebook_filename: str) -> typing.Dict[str, typing.Any]:
        resources = {}
        resources['unique_key'] = os.path.basename(notebook_filename)
        resources['output_files_dir'] = '%s_files' % os.path.basename(notebook_filename)
        resources['output_json_file'] = f'{os.path.basename(notebook_filename)}_out.json'
        resources['output_json_path'] = os.path.join(os.getcwd(), resources['output_json_file'])

        return resources

    def write_single_notebook(self, output: str, resources: ResourcesDict) -> None:
        # configure the writer build directory
        self.writer.build_directory = self._output_directory

        # write out the results
        self.writer.write(output, resources, notebook_name=resources['unique_key'])

    def init_destination(self) -> bool:
        """Initialize the destination for an assignment. Returns whether the
        assignment should actually be processed or not (i.e. whether the
        initialization was successful).

        """
        dest = self._output_directory
        source = self._input_directory

        # if we have specified --force, then always remove existing stuff
        if self.force:
            return True

        # if files exist in in the destination and force is not specified return false
        src_files = glob.glob(self._format_source())
        for src in src_files:
            file_name = os.path.join(dest, os.path.relpath(src, source))
            if os.path.exists(os.path.join(dest, file_name)):
                return False
        return True


    def set_permissions(self) -> None:
        self.log.info("Setting destination file permissions to %s", self.permissions)
        dest = os.path.normpath(self._output_directory)
        permissions = int(str(self.permissions), 8)
        for dirname, _, filenames in os.walk(dest):
            for filename in filenames:
                os.chmod(os.path.join(dirname, filename), permissions)
            # If groupshared, set dir permissions - see comment below.
            st_mode = os.stat(dirname).st_mode
            if self.coursedir.groupshared and st_mode & 0o2770 != 0o2770:
                try:
                    os.chmod(dirname, (st_mode|0o2770) & 0o2777)
                except PermissionError:
                    self.log.warning("Could not update permissions of %s to make it groupshared", dirname)
        # If groupshared, set write permissions on directories.  Directories
        # are created within ipython_genutils.path.ensure_dir_exists via
        # nbconvert.writer, (unless there are supplementary files) with a
        # default mode of 755 and there is no way to pass the mode arguments
        # all the way to there!  So we have to walk and fix.
        if self.coursedir.groupshared:
            # Root may be created in this step, and is not included above.
            rootdir = self.coursedir.format_path(self._output_directory, '.', '.')
            # Add 2770 to existing dir permissions (don't unconditionally override)
            st_mode = os.stat(rootdir).st_mode
            if st_mode & 0o2770 != 0o2770:
                try:
                    os.chmod(rootdir, (st_mode|0o2770) & 0o2777)
                except PermissionError:
                    self.log.warning("Could not update permissions of %s to make it groupshared", rootdir)

    def convert_single_notebook(self, notebook_filename: str) -> None:
        """
        Convert a single notebook.

        Performs the following steps:
            1. Initialize notebook resources
            2. Export the notebook to a particular format
            3. Write the exported notebook to file
        """
        self.log.info("Converting notebook %s", notebook_filename)
        resources = self.init_single_notebook_resources(notebook_filename)
        output, resources = self.exporter.from_filename(notebook_filename, resources=resources)
        self.write_single_notebook(output, resources)

    def convert_notebooks(self) -> None:
        errors = []

        def _handle_failure(exception) -> None:
            dest = os.path.normpath(self._output_directory)
            rmtree(dest)

        # initialize the list of notebooks and the exporter
        self.notebooks = sorted(self.notebooks)

        try:
            # determine whether we actually even want to process the notebooks
            should_process = self.init_destination()
            if not should_process:
                return

            self.run_pre_convert_hook()

            # convert all the notebooks
            for notebook_filename in self.notebooks:
                self.convert_single_notebook(notebook_filename)

            # set assignment permissions
            self.set_permissions()
            self.run_post_convert_hook()

        except UnresponsiveKernelError as e:
            self.log.error(
                "While processing files %s, the kernel became "
                "unresponsive and we could not interrupt it. This probably "
                "means that the students' code has an infinite loop that "
                "consumes a lot of memory or something similar. nbgrader "
                "doesn't know how to deal with this problem, so you will "
                "have to manually edit the students' code (for example, to "
                "just throw an error rather than enter an infinite loop). ",
                self._format_source())
            errors.append(e)
            _handle_failure(e)

        except sqlalchemy.exc.OperationalError as e:
            _handle_failure(e)
            self.log.error(traceback.format_exc())
            msg = (
                "There was an error accessing the nbgrader database. This "
                "may occur if you recently upgraded nbgrader. To resolve "
                "the issue, first BACK UP your database and then run the "
                "command `nbgrader db upgrade`."
            )
            self.log.error(msg)
            raise GraderConvertException(msg)

        except SchemaTooOldError as e:
            _handle_failure(e)
            msg = (
                "One or more notebooks in the assignment use an old version \n"
                "of the nbgrader metadata format. Please **back up your class files \n"
                "directory** and then update the metadata using:\n\nnbgrader update .\n"
            )
            self.log.error(msg)
            raise GraderConvertException(msg)

        except SchemaTooNewError as e:
            _handle_failure(e)
            msg = (
                "One or more notebooks in the assignment use an newer version \n"
                "of the nbgrader metadata format. Please update your version of \n"
                "nbgrader to the latest version to be able to use this notebook.\n"
            )
            self.log.error(msg)
            raise GraderConvertException(msg)

        except KeyboardInterrupt as e:
            _handle_failure(e)
            self.log.error("Canceled")
            raise

        except Exception as e:
            self.log.error("There was an error processing files: %s", self._format_source())
            self.log.error(traceback.format_exc())
            errors.append(e)
            _handle_failure(e)

        if len(errors) > 0:
            for assignment_id, student_id in errors:
                self.log.error(
                    "There was an error processing assignment '{}' for student '{}'".format(
                        assignment_id, student_id))

            if self.logfile:
                msg = (
                    "Please see the error log ({}) for details on the specific "
                    "errors on the above failures.".format(self.logfile))
            else:
                msg = (
                    "Please see the the above traceback for details on the specific "
                    "errors on the above failures.")

            self.log.error(msg)
            raise GraderConvertException(msg)

    def run_pre_convert_hook(self):
        if self.pre_convert_hook:
            self.log.info('Running pre-convert hook')
            try:
                self.pre_convert_hook(
                    assignment=self.coursedir.assignment_id,
                    student=self.coursedir.student_id,
                    notebooks=self.notebooks)
            except Exception:
                self.log.info('Pre-convert hook failed', exc_info=True)

    def run_post_convert_hook(self):
        if self.post_convert_hook:
            self.log.info('Running post-convert hook')
            try:
                self.post_convert_hook(
                    assignment=self.coursedir.assignment_id,
                    student=self.coursedir.student_id,
                    notebooks=self.notebooks)
            except Exception:
                self.log.info('Post-convert hook failed', exc_info=True)