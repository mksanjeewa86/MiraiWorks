'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Input,
  Label,
  LoadingSpinner,
  Checkbox,
  Badge,
  Switch,
} from '@/components/ui';
import { ArrowLeft, Send, Search, Users, Calendar } from 'lucide-react';
import Link from 'next/link';
import { useExam, useExamAssignments, useAssignmentMutations } from '@/hooks/useExams';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { toast } from 'sonner';
import { apiClient } from '@/api/apiClient';
import { API_ENDPOINTS } from '@/api/config';

interface Candidate {
  id: number;
  email: string;
  full_name: string;
  company_name?: string;
}

function AssignExamContent() {
  const params = useParams();
  const router = useRouter();
  const examId = parseInt(params.id as string);

  const { exam, loading: examLoading } = useExam(examId);
  const {
    assignments,
    loading: assignmentsLoading,
    refetch: refetchAssignments,
  } = useExamAssignments(examId);
  const { createAssignments, loading: assigning } = useAssignmentMutations();

  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loadingCandidates, setLoadingCandidates] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCandidates, setSelectedCandidates] = useState<number[]>([]);

  // Assignment settings
  const [dueDate, setDueDate] = useState<string>('');
  const [customTimeLimit, setCustomTimeLimit] = useState<number | null>(null);
  const [customMaxAttempts, setCustomMaxAttempts] = useState<number | null>(null);
  const [sendEmail, setSendEmail] = useState<boolean>(true);

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    setLoadingCandidates(true);
    try {
      const response = await apiClient.get<{ users: Candidate[] }>(
        `${API_ENDPOINTS.USERS.BASE}?role=candidate&limit=1000`
      );
      setCandidates(response.data.users || []);
    } catch (error) {
      toast.error('Failed to load candidates');
    } finally {
      setLoadingCandidates(false);
    }
  };

  const handleToggleCandidate = (candidateId: number) => {
    setSelectedCandidates((prev) =>
      prev.includes(candidateId) ? prev.filter((id) => id !== candidateId) : [...prev, candidateId]
    );
  };

  const handleSelectAll = () => {
    const filteredIds = filteredCandidates.map((c) => c.id);
    setSelectedCandidates(filteredIds);
  };

  const handleDeselectAll = () => {
    setSelectedCandidates([]);
  };

  const handleAssign = async () => {
    if (selectedCandidates.length === 0) {
      toast.error('Please select at least one candidate');
      return;
    }

    try {
      await createAssignments(
        examId,
        {
          candidate_ids: selectedCandidates,
          due_date: dueDate || null,
          custom_time_limit_minutes: customTimeLimit,
          custom_max_attempts: customMaxAttempts,
        },
        sendEmail
      );

      setSelectedCandidates([]);
      refetchAssignments();
    } catch (error) {
      // Error already handled by hook
    }
  };

  const filteredCandidates = candidates.filter(
    (candidate) =>
      candidate.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      candidate.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get already assigned candidate IDs
  const assignedCandidateIds = new Set(assignments.map((a) => a.candidate_id));

  if (examLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner />
      </div>
    );
  }

  if (!exam) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Exam not found</h2>
        <Button asChild>
          <Link href="/admin/exams">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Exams
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="py-6">
        <div className="mb-6">
          <Button variant="ghost" asChild className="mb-2">
            <Link href="/admin/exams">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Exams
            </Link>
          </Button>
          <h1 className="text-3xl font-bold text-gray-900">Assign Exam</h1>
          <p className="text-gray-600">{exam.title} - Assign to candidates</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Select Candidates</CardTitle>
                    <CardDescription>Choose candidates to assign this exam</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={handleSelectAll}>
                      Select All
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleDeselectAll}>
                      Deselect All
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search by name or email..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                {loadingCandidates ? (
                  <div className="flex justify-center py-8">
                    <LoadingSpinner />
                  </div>
                ) : (
                  <div className="space-y-2 max-h-[500px] overflow-y-auto">
                    {filteredCandidates.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">No candidates found</div>
                    ) : (
                      filteredCandidates.map((candidate) => {
                        const isAssigned = assignedCandidateIds.has(candidate.id);
                        const isSelected = selectedCandidates.includes(candidate.id);

                        return (
                          <div
                            key={candidate.id}
                            className={`flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors ${
                              isAssigned ? 'bg-gray-50 border-gray-300' : ''
                            }`}
                          >
                            <div className="flex items-center gap-3 flex-1">
                              <Checkbox
                                checked={isSelected}
                                onCheckedChange={() => handleToggleCandidate(candidate.id)}
                                disabled={isAssigned}
                              />
                              <div>
                                <div className="font-medium text-gray-900">
                                  {candidate.full_name}
                                </div>
                                <div className="text-sm text-gray-500">{candidate.email}</div>
                              </div>
                            </div>
                            {isAssigned && (
                              <Badge variant="outline" className="bg-green-50 text-green-700">
                                Already Assigned
                              </Badge>
                            )}
                          </div>
                        );
                      })
                    )}
                  </div>
                )}

                <div className="mt-4 pt-4 border-t">
                  <div className="text-sm text-gray-600">
                    Selected: <span className="font-semibold">{selectedCandidates.length}</span>{' '}
                    candidate(s)
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Assignment Settings</CardTitle>
                <CardDescription>Configure exam parameters for candidates</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="due_date">Due Date (optional)</Label>
                  <Input
                    id="due_date"
                    type="datetime-local"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                  />
                  <p className="text-xs text-gray-500 mt-1">Leave empty for no deadline</p>
                </div>

                <div>
                  <Label htmlFor="custom_time_limit">Time Limit (minutes, optional)</Label>
                  <Input
                    id="custom_time_limit"
                    type="number"
                    value={customTimeLimit || ''}
                    onChange={(e) =>
                      setCustomTimeLimit(e.target.value ? parseInt(e.target.value) : null)
                    }
                    placeholder={`Default: ${exam.time_limit_minutes || 'No limit'}`}
                    min={1}
                  />
                  <p className="text-xs text-gray-500 mt-1">Override exam default time limit</p>
                </div>

                <div>
                  <Label htmlFor="custom_max_attempts">Max Attempts (optional)</Label>
                  <Input
                    id="custom_max_attempts"
                    type="number"
                    value={customMaxAttempts || ''}
                    onChange={(e) =>
                      setCustomMaxAttempts(e.target.value ? parseInt(e.target.value) : null)
                    }
                    placeholder={`Default: ${exam.max_attempts}`}
                    min={1}
                  />
                  <p className="text-xs text-gray-500 mt-1">Override exam default max attempts</p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t">
                  <div>
                    <Label htmlFor="send_email">Send Email Notifications</Label>
                    <p className="text-xs text-gray-500 mt-1">
                      Notify candidates via email when assigned
                    </p>
                  </div>
                  <Switch id="send_email" checked={sendEmail} onCheckedChange={setSendEmail} />
                </div>

                <Button
                  onClick={handleAssign}
                  disabled={assigning || selectedCandidates.length === 0}
                  className="w-full"
                  size="lg"
                >
                  <Send className="h-4 w-4 mr-2" />
                  {assigning
                    ? 'Assigning...'
                    : `Assign to ${selectedCandidates.length} Candidate(s)`}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Current Assignments</CardTitle>
              </CardHeader>
              <CardContent>
                {assignmentsLoading ? (
                  <LoadingSpinner />
                ) : assignments.length === 0 ? (
                  <div className="text-center py-4 text-gray-500 text-sm">No assignments yet</div>
                ) : (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                      <Users className="h-4 w-4" />
                      <span>{assignments.length} candidate(s) assigned</span>
                    </div>
                    <div className="max-h-48 overflow-y-auto space-y-1">
                      {assignments.slice(0, 10).map((assignment) => (
                        <div
                          key={assignment.id}
                          className="text-sm text-gray-600 p-2 bg-gray-50 rounded"
                        >
                          Assignment #{assignment.id}
                        </div>
                      ))}
                      {assignments.length > 10 && (
                        <div className="text-xs text-gray-500 text-center pt-2">
                          +{assignments.length - 10} more
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

export default function AssignExamPage() {
  return (
    <ProtectedRoute>
      <AssignExamContent />
    </ProtectedRoute>
  );
}
