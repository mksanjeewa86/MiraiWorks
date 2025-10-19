'use client';

import { useState } from 'react';
import { CheckCircle, XCircle, Send, Eye, EyeOff, Star, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui';
import { Textarea } from '@/components/ui';
import { Input } from '@/components/ui';
import { Badge } from '@/components/ui';
import { useToast } from '@/contexts/ToastContext';
import { useAuth } from '@/contexts/AuthContext';
import { todosApi } from '@/api/todos';
import type {
  Todo,
  TodoWithAssignedUser,
  AssignmentSubmission,
  AssignmentReview,
} from '@/types/todo';
import type { AssignmentWorkflowProps } from '@/types/components';

export default function AssignmentWorkflow({ todo, onUpdate }: AssignmentWorkflowProps) {
  const { showToast } = useToast();
  const { user } = useAuth();
  const [submitting, setSubmitting] = useState(false);
  const [submissionNotes, setSubmissionNotes] = useState('');
  const [reviewNotes, setReviewNotes] = useState('');
  const [reviewScore, setReviewScore] = useState<number | ''>('');

  if (!todo.is_assignment) {
    return null;
  }

  const isOwner = todo.owner_id === user?.id;
  const isDraft = todo.is_draft;
  const isPublished = todo.is_published;
  const canEditAssignee = todo.can_be_edited_by_assignee;
  const isSubmitted = todo.submitted_at !== null && todo.submitted_at !== undefined;
  const isReviewed = todo.reviewed_at !== null && todo.reviewed_at !== undefined;

  const handlePublish = async () => {
    if (!isOwner) return;
    setSubmitting(true);
    try {
      await todosApi.publishAssignment(todo.id);
      showToast({ type: 'success', title: 'Assignment published successfully' });
      onUpdate();
    } catch (error: any) {
      showToast({
        type: 'error',
        title: error?.response?.data?.detail || 'Failed to publish assignment',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleMakeDraft = async () => {
    if (!isOwner) return;
    setSubmitting(true);
    try {
      await todosApi.makeDraftAssignment(todo.id);
      showToast({ type: 'success', title: 'Assignment made draft successfully' });
      onUpdate();
    } catch (error: any) {
      showToast({
        type: 'error',
        title: error?.response?.data?.detail || 'Failed to make assignment draft',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = async () => {
    if (!isOwner || !canEditAssignee) return;
    setSubmitting(true);
    try {
      const submission: AssignmentSubmission = {
        notes: submissionNotes.trim() || undefined,
      };
      await todosApi.submitAssignment(todo.id, submission);
      showToast({ type: 'success', title: 'Assignment submitted for review' });
      setSubmissionNotes('');
      onUpdate();
    } catch (error: any) {
      showToast({
        type: 'error',
        title: error?.response?.data?.detail || 'Failed to submit assignment',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleReview = async (approved: boolean) => {
    if (!isOwner) return;
    setSubmitting(true);
    try {
      const review: AssignmentReview = {
        approved,
        assessment: reviewNotes.trim() || undefined,
        score: typeof reviewScore === 'number' ? reviewScore : undefined,
      };
      await todosApi.reviewAssignment(todo.id, review);
      showToast({
        type: 'success',
        title: `Assignment ${approved ? 'approved' : 'rejected'} successfully`,
      });
      setReviewNotes('');
      setReviewScore('');
      onUpdate();
    } catch (error: any) {
      showToast({
        type: 'error',
        title: error?.response?.data?.detail || 'Failed to review assignment',
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-4 rounded-lg border border-blue-200 bg-blue-50 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="primary" className="text-xs">
            Assignment
          </Badge>
          {isSubmitted && !isReviewed && (
            <Badge variant="warning" className="text-xs">
              Awaiting Review
            </Badge>
          )}
          {isReviewed && (
            <Badge variant="success" className="text-xs">
              Reviewed
            </Badge>
          )}
        </div>

        {/* Owner Controls */}
        {isOwner && (
          <div className="flex items-center gap-2">
            {isDraft ? (
              <Button
                size="sm"
                variant="outline"
                onClick={handlePublish}
                disabled={submitting}
                className="text-xs"
              >
                <Eye className="h-3 w-3" />
                Publish
              </Button>
            ) : (
              <Button
                size="sm"
                variant="outline"
                onClick={handleMakeDraft}
                disabled={submitting}
                className="text-xs"
              >
                <EyeOff className="h-3 w-3" />
                Make Draft
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Draft Status Warning */}
      {isDraft && (
        <div className="rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          <div className="flex items-start gap-2">
            <EyeOff className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium">Draft Assignment</p>
              <p className="text-xs mt-1">
                This assignment is in draft mode. Publish it when ready.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Owner Submission */}
      {isOwner && canEditAssignee && !isSubmitted && isPublished && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-slate-700">Submit Assignment</h4>
          <Textarea
            placeholder="Add any notes about your submission (optional)..."
            value={submissionNotes}
            onChange={(e) => setSubmissionNotes(e.target.value)}
            rows={3}
            className="text-sm"
          />
          <Button size="sm" onClick={handleSubmit} disabled={submitting} className="w-full">
            <Send className="h-3 w-3" />
            Submit for Review
          </Button>
        </div>
      )}

      {/* Owner Review Section */}
      {isOwner && isSubmitted && !isReviewed && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-slate-700">Review Assignment</h4>

          <div className="grid gap-3">
            <Textarea
              placeholder="Assessment feedback for the assignee..."
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              rows={3}
              className="text-sm"
            />

            <Input
              type="number"
              label="Score (0-100)"
              placeholder="Optional numeric score"
              value={reviewScore}
              onChange={(e) => setReviewScore(e.target.value ? Number(e.target.value) : '')}
              min={0}
              max={100}
              leftIcon={<Star className="h-4 w-4" />}
            />
          </div>

          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleReview(true)}
              disabled={submitting}
              className="flex-1 text-green-700 border-green-300 hover:bg-green-50"
            >
              <CheckCircle className="h-3 w-3" />
              Approve
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleReview(false)}
              disabled={submitting}
              className="flex-1 text-red-700 border-red-300 hover:bg-red-50"
            >
              <XCircle className="h-3 w-3" />
              Reject
            </Button>
          </div>
        </div>
      )}

      {/* Assignment Result Display */}
      {isReviewed && todo.assignment_assessment && (
        <div className="rounded border border-blue-200 bg-blue-50 p-3 text-sm text-blue-800">
          <div className="flex items-start gap-2">
            <MessageSquare className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium">Review Feedback</p>
              <p className="text-xs mt-1">{todo.assignment_assessment}</p>
              {todo.assignment_score !== null && todo.assignment_score !== undefined && (
                <p className="text-xs mt-1 font-medium">Score: {todo.assignment_score}/100</p>
              )}
              {todo.reviewed_at && (
                <p className="text-xs mt-1 opacity-75">
                  Reviewed {new Date(todo.reviewed_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
