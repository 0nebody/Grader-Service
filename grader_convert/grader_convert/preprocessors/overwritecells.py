

from typing import Any, Tuple

from nbconvert.exporters.exporter import ResourcesDict
from nbformat.notebooknode import NotebookNode
from nbformat.v4.nbbase import validate

from grader_convert.gradebook.gradebook import Gradebook, MissingEntry
from grader_convert import utils
from grader_convert.preprocessors.base import NbGraderPreprocessor

class OverwriteCells(NbGraderPreprocessor):
    """A preprocessor to overwrite information about grade and solution cells."""

    def preprocess(
        self, nb: NotebookNode, resources: ResourcesDict
    ) -> Tuple[NotebookNode, ResourcesDict]:
        # pull information from the resources
        self.notebook_id = resources["unique_key"]
        self.json_path = resources["output_json_path"]
        self.gradebook = Gradebook(self.json_path)

        with self.gradebook:
            nb, resources = super(OverwriteCells, self).preprocess(nb, resources)

        return nb, resources

    def update_cell_type(self, cell: NotebookNode, cell_type: str) -> None:
        if cell.cell_type == cell_type:
            return
        elif cell_type == "code":
            cell.cell_type = "code"
            cell.outputs = []
            cell.execution_count = None

        elif cell_type == "markdown":
            cell.cell_type = "markdown"
            if "outputs" in cell:
                del cell["outputs"]
            if "execution_count" in cell:
                del cell["execution_count"]
        elif cell_type == "raw":
            cell.cell_type = "raw"


    def report_change(self, name: str, attr: str, old: Any, new: Any) -> None:
        self.log.warning(
            "Attribute '%s' for cell %s has changed! (should be: %s, got: %s)",
            attr,
            name,
            old,
            new,
        )

    def preprocess_cell(
        self, cell: NotebookNode, resources: ResourcesDict, cell_index: int
    ) -> Tuple[NotebookNode, ResourcesDict]:
        grade_id = cell.metadata.get("nbgrader", {}).get("grade_id", None)
        if grade_id is None:
            return cell, resources

        try:
            source_cell = self.gradebook.find_source_cell(grade_id, self.notebook_id)
        except MissingEntry:
            self.log.warning(
                "Cell '{}' does not exist in the properties".format(grade_id)
            )
            del cell.metadata.nbgrader["grade_id"]
            return cell, resources

        # check that the cell type hasn't changed
        if cell.cell_type != source_cell.cell_type:
            self.report_change(
                grade_id, "cell_type", source_cell.cell_type, cell.cell_type
            )
            self.update_cell_type(cell, source_cell.cell_type)

        # check that the locked status hasn't changed
        if utils.is_locked(cell) != source_cell.locked:
            self.report_change(
                grade_id, "locked", source_cell.locked, utils.is_locked(cell)
            )
            cell.metadata.nbgrader["locked"] = source_cell.locked

        # if it's a grade cell, check that the max score hasn't changed
        if utils.is_grade(cell):
            grade_cell = self.gradebook.find_graded_cell(grade_id, self.notebook_id)
            old_points = float(grade_cell.max_score)
            new_points = float(cell.metadata.nbgrader["points"])

            if old_points != new_points:
                self.report_change(grade_id, "points", old_points, new_points)
                cell.metadata.nbgrader["points"] = old_points

        # always update the checksum, just in case
        cell.metadata.nbgrader["checksum"] = source_cell.checksum

        # if it's locked, check that the checksum hasn't changed
        if source_cell.locked:
            old_checksum = source_cell.checksum
            new_checksum = utils.compute_checksum(cell)
            if old_checksum != new_checksum:
                self.report_change(grade_id, "checksum", old_checksum, new_checksum)
                cell.source = source_cell.source
                # double check the the checksum is correct now
                if utils.compute_checksum(cell) != source_cell.checksum:
                    raise RuntimeError(
                        "Inconsistent checksums for cell {}".format(source_cell.name)
                    )

        return cell, resources
