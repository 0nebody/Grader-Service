import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Collapse,
  LinearProgress,
  Typography
} from '@mui/material';
import * as React from 'react';
import { Assignment } from '../../model/assignment';
import { Lecture } from '../../model/lecture';
import { getAllAssignments } from '../../services/assignments.service';
import { AssignmentComponent } from './assignment';

interface ILectureComponentProps {
  lecture: Lecture;
  root: HTMLElement;
  open?: boolean;
}

export const LectureComponent = (props: ILectureComponentProps) => {
  const [lecture, setLecture] = React.useState(props.lecture);
  const [assignments, setAssignments] = React.useState(null);
  const [expanded, setExpanded] = React.useState(props.open);

  React.useEffect(() => {
    getAllAssignments(lecture.id).then(response => {
      setAssignments(response);
    });
  }, []);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };
  if (assignments === null) {
    return (
      <div>
        <Card>
          <LinearProgress />
        </Card>
      </div>
    );
  }
  return (
    <div>
      <Card
        sx={{ backgroundColor: expanded ? '#fafafa' : 'background.paper' }}
        elevation={expanded ? 0 : 2}
        className="lecture-card"
      >
        <CardContent sx={{ mb: -1, display: 'flex' }}>
          <Typography variant={'h5'} sx={{ mr: 2 }}>
            {lecture.name}
          </Typography>
        </CardContent>

        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <CardContent>
            <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
              {assignments.map((el: Assignment) => (
                <AssignmentComponent
                  lecture={lecture}
                  assignment={el}
                  root={props.root}
                />
              ))}
            </Box>
          </CardContent>
        </Collapse>
        <CardActions>
          <Button size="small" sx={{ ml: 'auto' }} onClick={handleExpandClick}>
            {(expanded ? 'Hide' : 'Show') + ' Assignments'}
          </Button>
        </CardActions>
      </Card>
    </div>
  );
};
