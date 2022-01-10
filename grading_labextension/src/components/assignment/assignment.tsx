import * as React from 'react';
import {
  Box,
  Button,
  Card,
  CardActionArea,
  CardActions,
  CardContent,
  Chip, Divider,
  Stack,
  Typography
} from '@mui/material';
import {red} from "@mui/material/colors";

import CheckCircleOutlineOutlinedIcon from "@mui/icons-material/CheckCircleOutlineOutlined";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";


import {Assignment} from '../../model/assignment';
import LoadingOverlay from '../util/overlay';
import {Lecture} from '../../model/lecture';
import {getAllSubmissions} from '../../services/submissions.service';
import {getAssignment} from '../../services/assignments.service';
import {DeadlineComponent} from '../util/deadline';
import {AssignmentModalComponent} from './assignment-modal';
import {Submission} from '../../model/submission';
import {User} from '../../model/user';
import {getFiles} from "../../services/file.service";

interface IAssignmentComponentProps {
  lecture: Lecture;
  assignment: Assignment;
  root: HTMLElement;
}

export const AssignmentComponent = (props: IAssignmentComponentProps) => {
  const [assignment, setAssignment] = React.useState(props.assignment);
  const [displayAssignment, setDisplayAssignment] = React.useState(false);
  const [submissions, setSubmissions] = React.useState([] as Submission[]);
  const [hasFeedback, setHasFeedback] = React.useState(false);
  const [files, setFiles] = React.useState([]);
  React.useEffect(() => {
    getAllSubmissions(props.lecture, assignment, false, false).then(
      response => {
        setSubmissions(response[0].submissions);
        setHasFeedback(submissions.reduce(
          (accum: boolean, curr: Submission) =>
            accum || curr.feedback_available,
          false
        ))
      }
    );
    getFiles(`${props.lecture.code}/${assignment.name}`).then(files => {
      setFiles(files)
    })
  }, [props]);

  const onAssignmentClose = async () => {
    setDisplayAssignment(false);
    setAssignment(await getAssignment(props.lecture.id, assignment));
    const submissions = await getAllSubmissions(props.lecture, assignment, false, false);
    setSubmissions(submissions[0].submissions);
  };

  return (
    <Box>
      <Card
        sx={{maxWidth: 200, minWidth: 200, m: 1.5}}
        onClick={e => setDisplayAssignment(true)}
      >
        <CardActionArea>
          <CardContent>
            <Typography variant="h5" component="div">
              {assignment.name}
            </Typography>
            <Typography sx={{fontSize: 14}} color="text.secondary" gutterBottom>
              {files.length + ' File' + (files.length === 1 ? '' : 's')}
              {assignment.status === 'released' ? null : (
                <Typography sx={{fontSize: 12, display: "inline-block", color: red[500], float: "right"}}>
                  Not Released
                </Typography>
              )}
            </Typography>
            <Divider sx={{mt: 1, mb: 1}}/>

            <Typography sx={{fontSize: 16, mt: 1, ml: 0.5}}>
              {submissions.length}
              <Typography
                color="text.secondary"
                sx={{
                  display: "inline-block",
                  ml: 0.75,
                  fontSize: 14
                }}
              >
                {'Submission' + (submissions.length === 1 ? '' : 's')}
              </Typography>
            </Typography>
            <Typography sx={{fontSize: 16, mt: 0.25}}>
              {hasFeedback
                ? <CheckCircleOutlineOutlinedIcon sx={{fontSize: 16, mr: 0.5, mb: -0.35}}/>
                : <CancelOutlinedIcon sx={{fontSize: 16, mr: 0.5, mb: -0.35}}/>
              }
              <Typography
                color="text.secondary"
                sx={{
                  display: "inline-block",
                  fontSize: 14
                }}
              >
                {(hasFeedback ? 'Has' : 'No') + ' Feedback'}
              </Typography>
            </Typography>
          </CardContent>
          <DeadlineComponent due_date={assignment.due_date} compact={false} component={'card'}/>
        </CardActionArea>
      </Card>
      <LoadingOverlay
        onClose={onAssignmentClose}
        open={displayAssignment}
        container={props.root}
        transition="zoom"
      >
        <AssignmentModalComponent
          lecture={props.lecture}
          assignment={assignment}
          submissions={submissions}
        />
      </LoadingOverlay>
    </Box>
  );
};