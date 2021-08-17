from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Set, Type, List
from enum import Enum


@dataclass
class BaseModel:
    def __post_init__(self):
        self._type = self.__class__.__name__

    @classmethod
    def empty_dict(cls: Type["BaseModel"]) -> dict:
        fields = cls.__dataclass_fields__.keys()
        return {f: None for f in fields}

    def to_dict(self) -> dict:
        d = asdict(self)
        d["_type"] = self.__class__.__name__
        return d

    @classmethod
    def from_dict(cls: Type["BaseModel"], d: dict) -> Type["BaseModel"]:
        d_no_type = {k: v for k, v in d.items() if k != "_type"}
        return cls(**d_no_type)


@dataclass
class IDMixin:
    id: str


@dataclass
class NameMixin:
    name: str


@dataclass
class NotebookRelashionship:
    notebook_id: str


@dataclass
class CellRelashionship:
    cell_id: str


@dataclass
class Grade(BaseModel, IDMixin, NotebookRelashionship, CellRelashionship):
    """Representation of a grade assigned to the submitted version of a grade cell."""

    auto_score: float
    manual_score: float
    extra_credit: float
    needs_manual_grade: bool

    @property
    def score(self) -> float:
        """
        The overall score, computed automatically from the
        :attr:`~models.Grade.auto_score` and :attr:`~models.Grade.manual_score`
        values. If neither are set, the score is zero. If both are set, then the
        manual score takes precedence. If only one is set, then that value is used
        for the score
        """
        if self.manual_score is None and self.auto_score is None:
            return 0.0
        elif self.manual_score is None:
            return self.auto_score
        elif self.auto_score is None:
            return self.manual_score
        else:
            return self.manual_score

    #: The maximum possible score that can be assigned, inherited from
    #: :class:`~GradeCell`
    # TODO: how to keep the values default None but don't have them as class variables?
    max_score_gradecell: float = None
    max_score_taskcell: float = None

    @property
    def max_score(self):
        if self.max_score_taskcell:
            return self.max_score_taskcell
        else:
            return self.max_score_gradecell

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["max_score"] = self.max_score
        return d


@dataclass
class Comment(BaseModel, IDMixin, NotebookRelashionship, CellRelashionship):
    auto_comment: str
    manual_comment: str

    @property
    def comment(self) -> Optional[str]:
        if self.manual_comment is None:
            return self.auto_comment
        else:
            return self.manual_comment


class CellType(Enum):
    "code"
    "markdown"
    "raw"


@dataclass
class BaseCell(BaseModel, IDMixin, NameMixin, NotebookRelashionship):
    grade: Grade  # we can have only one grade
    comment: Comment  # we can have only one comment since we only process a single notebook

    @classmethod
    def from_dict(cls: Type["BaseCell"], d: dict) -> Type["BaseCell"]:
        if d["_type"] == "GradeCell":
            return GradeCell.from_dict(d)
        elif d["_type"] == "SolutionCell":
            return SolutionCell.from_dict(d)
        elif d["_type"] == "TaskCell":
            return TaskCell.from_dict(d)
        elif d["_type"] == "SourceCell":
            return SourceCell.from_dict(d)


@dataclass
class GradedMixin:
    max_score: float
    cell_type: CellType


@dataclass
class GradeCell(BaseCell, GradedMixin):
    @classmethod
    def from_dict(cls: Type["BaseCell"], d: dict) -> Type["BaseCell"]:
        grade = Grade.from_dict(d["grade"])
        comment = Comment.from_dict(d["comment"])
        return GradeCell(
            max_score=d["max_score"],
            cell_type=d["cell_type"],
            id=d["id"],
            notebook_id=d["notebook_id"],
            name=d["name"],
            grade=grade,
            comment=comment,
        )


@dataclass
class SolutionCell(BaseCell):
    @classmethod
    def from_dict(cls: Type["BaseCell"], d: dict) -> Type["BaseCell"]:
        grade = Grade.from_dict(d["grade"])
        comment = Comment.from_dict(d["comment"])
        return SolutionCell(
            id=d["id"],
            notebook_id=d["notebook_id"],
            name=d["name"],
            grade=grade,
            comment=comment,
        )


@dataclass
class TaskCell(BaseCell, GradedMixin):
    @classmethod
    def from_dict(cls: Type["BaseCell"], d: dict) -> Type["BaseCell"]:
        grade = Grade.from_dict(d["grade"])
        comment = Comment.from_dict(d["comment"])
        return GradeCell(
            max_score=d["max_score"],
            cell_type="code",  # cell_type from GradedMixin should always be 'code'
            id=d["id"],
            notebook_id=d["notebook_id"],
            name=d["name"],
            grade=grade,
            comment=comment,
        )


@dataclass
class SourceCell(BaseModel, IDMixin, NameMixin, NotebookRelashionship):
    cell_type: CellType

    #: Whether the cell is locked (e.g. the source saved in the database should
    #: be used to overwrite the source of students' cells)
    locked: bool

    #: The source code or text of the cell
    source: str

    #: A checksum of the cell contents. This should usually be computed
    #: using :func:`utils.compute_checksum`
    checksum: str

    @classmethod
    def from_dict(cls: Type["BaseModel"], d: dict) -> Type["BaseModel"]:
        return super().from_dict(d)


@dataclass
class Notebook(BaseModel, IDMixin, NameMixin):
    kernelspec: str
    base_cells: Dict[str, Type[BaseCell]]
    src_cells: Dict[str, Type[SourceCell]]

    @property
    def grade_cells(self) -> List[GradeCell]:
        return [x for x in self.base_cells.values() if isinstance(x, GradeCell)]

    @property
    def solution_cells(self) -> List[SolutionCell]:
        return [x for x in self.base_cells.values() if isinstance(x, SolutionCell)]

    @property
    def task_cells(self) -> List[TaskCell]:
        return [x for x in self.base_cells.values() if isinstance(x, TaskCell)]

    @property
    def source_cells(self) -> List[SourceCell]:
        return [x for x in self.src_cells.values()]

    @classmethod
    def from_dict(cls: Type["Notebook"], d: dict) -> Type["Notebook"]:
        bc = {id: BaseCell.from_dict(v) for id, v in d["base_cells"].items()}
        sc = {id: SourceCell.from_dict(v) for id, v in d["_source_cells"]}
        return Notebook(
            kernelspec=d["kernelspec"],
            base_cells=bc,
            id=d["id"],
            name=d["name"],
            src_cells=sc,
        )

    def to_dict(self) -> dict:
        return {
            "kernelspec": self.kernelspec,
            "base_cells": {k: v.to_dict() for k, v in self.base_cells.items()},
            "src_cells": {k: v.to_dict() for k, v in self.src_cells.items()},
        }


@dataclass
class GradeBookModel(BaseModel):
    notebooks: Dict[str, Notebook]

    @classmethod
    def from_dict(cls: Type["GradeBookModel"], d: dict) -> "GradeBookModel":
        ns = {id: Notebook.from_dict(v) for id, v in d["notebooks"].items()}
        return GradeBookModel(notebooks=ns)

    def to_dict(self) -> dict:
        return {"notebooks": {k: v.to_dict() for k, v in self.notebooks.items()}}
