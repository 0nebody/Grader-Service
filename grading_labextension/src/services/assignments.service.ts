import { Assignment } from '../model/assignment';
import { Lecture } from '../model/lecture';
import { request, HTTPMethod } from './request.service'

export function createAssignment(lectureId: number, assignment: Assignment): Promise<Assignment> {
  return request<Assignment>(HTTPMethod.POST, `/lectures/${lectureId}/assignments`, assignment)
}

export function getAllAssignments(lectureId: number): Promise<Assignment[]> {
  return request<Assignment[]>(HTTPMethod.GET, `/lectures/${lectureId}/assignments`)
}

export function getAssignment(lectureId: number, assignment: Assignment): Promise<Assignment> {
  return request<Assignment>(HTTPMethod.GET, `/lectures/${lectureId}/assignments/${assignment.id}`)
}

export function updateAssignment(lectureId: number, assignment: Assignment): Promise<Assignment> {
  return request<Assignment>(HTTPMethod.PUT, `/lectures/${lectureId}/assignments/${assignment.id}`, assignment)
}

export function generateAssignment(lectureId: number, assignment: Assignment): Promise<any> {
  return request<any>(HTTPMethod.PUT,`/lectures/${lectureId}/assignments/${assignment.id}/generate`)
}

export function fetchAssignment(lectureId: number, assignmentId: number, instructor: boolean = false, metadataOnly: boolean = false): Promise<Assignment> {
  let url = `/lectures/${lectureId}/assignments/${assignmentId}`;
  if (instructor || metadataOnly) {
    let searchParams = new URLSearchParams({
      "instructor-version": String(instructor),
      "metadata-only": String(metadataOnly)
    })
    url += '?' + searchParams;
  }

  return request<Assignment>(HTTPMethod.GET, url)
}

export function deleteAssignment(lectureId: number, assignmentId: number): Promise<void> {
  return request<void>(HTTPMethod.DELETE, `/lectures/${lectureId}/assignments/${assignmentId}`)
}

export function pushAssignment(lectureId: number, assignmentId: number, repoType: string): Promise<void> {
  return request<void>(HTTPMethod.PUT, `/lectures/${lectureId}/assignments/${assignmentId}/push/${repoType}`)
}

export function pullAssignment(lectureId: number, assignmentId: number, repoType: string): Promise<void> {
  return request<void>(HTTPMethod.GET, `/lectures/${lectureId}/assignments/${assignmentId}/pull/${repoType}`)
}

