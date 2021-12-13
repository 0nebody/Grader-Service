import { Cell } from '@jupyterlab/cells';
import { PanelLayout } from "@lumino/widgets";
import { GradeBook } from "../../../services/gradebook";
import { getProperties, getSubmission, updateProperties, updateSubmission } from "../../../services/submissions.service";
import { CellWidget } from "../create-assignment/cellwidget";
import { CellPlayButton } from "../create-assignment/widget";
import { ImodeSwitchProps } from "../slider";
import { GradeCellWidget } from "./grade-cell-widget";
import { GradeCommentCellWidget } from "./grade-comment-cell-widget";
import { showErrorMessage } from '@jupyterlab/apputils';
import { Button, Intent, Switch } from '@blueprintjs/core';
import * as React from 'react';
import { Notebook, NotebookPanel } from '@jupyterlab/notebook';
import { Lecture } from '../../../model/lecture';
import { Assignment } from '../../../model/assignment';
import { IconNames } from '@blueprintjs/icons';
import { getAllAssignments } from '../../../services/assignments.service';
import { getAllLectures } from '../../../services/lectures.service';
import { UserPermissions, Scope } from '../../../services/permission.service';


export class GradingModeSwitch extends React.Component<ImodeSwitchProps> {

  
    public state = {
        mode: false,
        saveButtonText: "Save",
        transition: "show"
      };
      protected notebook: Notebook;
      protected notebookpanel: NotebookPanel;
      public lecture: Lecture;
      public assignment: Assignment;
      public gradeBook: GradeBook;
      public onChange: any;
      public subID: number;
      public notebookPaths: string[];
    
      public constructor(props: ImodeSwitchProps) {
        super(props);
        this.state.mode = props.mode || false;
        this.notebook = props.notebook;
        this.notebookpanel = props.notebookpanel;
        this.notebookPaths = this.notebookpanel.context.contentsModel.path.split("/");
        this.subID = +this.notebookPaths[3];
        this.onChange = this.props.onChange;
      }
    
      public async componentDidMount() {
        const lectures = await getAllLectures();
        this.lecture = lectures.find(l => l.code === this.notebookPaths[1]);
        const assignments = await getAllAssignments(this.lecture.id);
        this.assignment = assignments.find(a => a.name === this.notebookPaths[2]);
    
        const properties = await getProperties(this.lecture.id, this.assignment.id, this.subID);
        this.gradeBook = new GradeBook(properties);
      }

    private async saveProperties() {
        this.setState({ transition: "" })
        this.setState({ saveButtonText: "Saving" })
        try {
          await updateProperties(this.lecture.id, this.assignment.id, this.subID, this.gradeBook.properties);
          this.setState({ saveButtonText: "Saved" })
          //console.log("saved")
          setTimeout(() => this.setState({ saveButtonText: "Save", transition: "show" }), 2000);
          const submission = await getSubmission(this.lecture.id,this.assignment.id,this.subID);
          console.log(submission)
          submission.manual_status = "manually_graded"
          updateSubmission(this.lecture.id,this.assignment.id,this.subID, submission);
        } catch (err) {
          this.setState({ saveButtonText: "Save", transition: "show" });
          showErrorMessage("Error saving properties", err);
        }
    }

    protected handleChange = async () => {
        const properties = await getProperties(this.lecture.id, this.assignment.id, this.subID);
        this.gradeBook = new GradeBook(properties);
        this.setState({ mode: !this.state.mode }, () => {
            this.onChange(this.state.mode);
            this.notebook.widgets.map((c: Cell) => {
                const currentLayout = c.layout as PanelLayout;
                if (this.state.mode) {
                    currentLayout.insertWidget(0, new GradeCellWidget(c, this.gradeBook, this.notebookPaths[4].split(".").slice(0, -1).join(".")));
                    currentLayout.addWidget(new GradeCommentCellWidget(c, this.gradeBook, this.notebookPaths[4].split(".").slice(0, -1).join(".")))
                } else {
                    currentLayout.widgets.map(w => {
                    if (w instanceof GradeCellWidget || w instanceof GradeCommentCellWidget) {
                        currentLayout.removeWidget(w);
                        }
                    });
                }
            });
        });  
    }

    public render() {
        return (<span id="manual-grade-switch">
        <Switch
          checked={this.state.mode}
          label="Gradingmode"
          onChange={this.handleChange}
        />
        <Button className="assignment-button" onClick={() => this.saveProperties()} icon={IconNames.FLOPPY_DISK} outlined intent={Intent.SUCCESS}>
          <span className={this.state.transition} >{this.state.saveButtonText}</span>
        </Button>
      </span>);
    }

}