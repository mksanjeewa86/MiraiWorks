'use client';

import { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Textarea,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui';
import {
  Check,
  X,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Building2,
  User,
  MessageSquare,
} from 'lucide-react';
import { LoadingSpinner } from '@/components/ui';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import {
  useAllPlanChangeRequests,
  useReviewPlanChangeRequest,
} from '@/hooks/useSubscription';
import { PlanChangeRequestWithDetails } from '@/types/subscription';

function PlanRequestsAdminContent() {
  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const { requests, loading, refetch } = useAllPlanChangeRequests(statusFilter);
  const { reviewRequest } = useReviewPlanChangeRequest();

  const [selectedRequest, setSelectedRequest] = useState<PlanChangeRequestWithDetails | null>(null);
  const [reviewMessage, setReviewMessage] = useState('');
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewAction, setReviewAction] = useState<'approved' | 'rejected'>('approved');

  const handleReview = async () => {
    if (!selectedRequest) return;

    try {
      await reviewRequest(selectedRequest.id, reviewAction, reviewMessage);
      setShowReviewModal(false);
      setSelectedRequest(null);
      setReviewMessage('');
      refetch();
    } catch (error) {
      // Error handled by hook
    }
  };

  const formatPrice = (price: string | number) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
    }).format(numPrice);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return (
          <Badge variant="outline" className="text-yellow-600">
            <Clock className="h-3 w-3 mr-1" />
            Pending
          </Badge>
        );
      case 'approved':
        return (
          <Badge variant="outline" className="text-green-600">
            <Check className="h-3 w-3 mr-1" />
            Approved
          </Badge>
        );
      case 'rejected':
        return (
          <Badge variant="outline" className="text-red-600">
            <X className="h-3 w-3 mr-1" />
            Rejected
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getRequestTypeIcon = (currentPrice: string, requestedPrice: string) => {
    const current = parseFloat(currentPrice);
    const requested = parseFloat(requestedPrice);

    if (requested > current) {
      return <ArrowUpRight className="h-5 w-5 text-green-600" />;
    }
    return <ArrowDownRight className="h-5 w-5 text-blue-600" />;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Plan Change Requests</h1>
          <p className="text-muted-foreground">
            Review and approve subscription plan changes
          </p>
        </div>

        {/* Filter */}
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="approved">Approved</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
            <SelectItem value="all">All Requests</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Requests List */}
      {requests.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Clock className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">
              No {statusFilter !== 'all' ? statusFilter : ''} requests found
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {requests.map((request) => {
            const isUpgrade =
              parseFloat(request.requested_plan?.price_monthly?.toString() || '0') >
              parseFloat(request.current_plan?.price_monthly?.toString() || '0');

            return (
              <Card key={request.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {request.current_plan && request.requested_plan && (
                          <>
                            {getRequestTypeIcon(
                              request.current_plan.price_monthly.toString(),
                              request.requested_plan.price_monthly.toString()
                            )}
                            <CardTitle className="text-xl">
                              {request.current_plan.display_name} →{' '}
                              {request.requested_plan.display_name}
                            </CardTitle>
                          </>
                        )}
                      </div>

                      <div className="grid md:grid-cols-2 gap-4 mt-4">
                        {/* Company Info */}
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Building2 className="h-4 w-4" />
                          <span>{request.company_name || 'Unknown Company'}</span>
                        </div>

                        {/* Requester Info */}
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <User className="h-4 w-4" />
                          <span>
                            Requested by {request.requester_name || 'Unknown User'}
                          </span>
                        </div>

                        {/* Request Date */}
                        <div className="text-sm text-muted-foreground">
                          {new Date(request.created_at).toLocaleDateString('ja-JP', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                          })}
                        </div>

                        {/* Price Difference */}
                        {request.current_plan && request.requested_plan && (
                          <div className="text-sm font-medium">
                            {formatPrice(request.current_plan.price_monthly)} →{' '}
                            {formatPrice(request.requested_plan.price_monthly)}
                          </div>
                        )}
                      </div>
                    </div>

                    {getStatusBadge(request.status)}
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Request Message */}
                  {request.request_message && (
                    <div className="bg-muted/50 p-3 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <MessageSquare className="h-4 w-4 text-muted-foreground" />
                        <p className="text-sm font-medium">Request Message</p>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {request.request_message}
                      </p>
                    </div>
                  )}

                  {/* Review Message */}
                  {request.review_message && (
                    <div className="bg-muted/50 p-3 rounded-lg">
                      <p className="text-sm font-medium mb-1">
                        Review by {request.reviewer_name || 'Admin'}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {request.review_message}
                      </p>
                      {request.reviewed_at && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(request.reviewed_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Actions */}
                  {request.status === 'pending' && (
                    <div className="flex gap-2">
                      <Button
                        variant="default"
                        className="flex-1"
                        onClick={() => {
                          setSelectedRequest(request);
                          setReviewAction('approved');
                          setShowReviewModal(true);
                        }}
                      >
                        <Check className="h-4 w-4 mr-2" />
                        Approve
                      </Button>
                      <Button
                        variant="destructive"
                        className="flex-1"
                        onClick={() => {
                          setSelectedRequest(request);
                          setReviewAction('rejected');
                          setShowReviewModal(true);
                        }}
                      >
                        <X className="h-4 w-4 mr-2" />
                        Reject
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Review Modal */}
      {showReviewModal && selectedRequest && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <Card className="max-w-md w-full">
            <CardHeader>
              <CardTitle>
                {reviewAction === 'approved' ? 'Approve' : 'Reject'} Request
              </CardTitle>
              <CardDescription>
                {selectedRequest.current_plan?.display_name} →{' '}
                {selectedRequest.requested_plan?.display_name}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">
                  Review Message (optional)
                </label>
                <Textarea
                  value={reviewMessage}
                  onChange={(e) => setReviewMessage(e.target.value)}
                  placeholder={
                    reviewAction === 'approved'
                      ? 'Approved. Welcome to the new plan!'
                      : 'Reason for rejection...'
                  }
                  rows={3}
                />
              </div>

              {reviewAction === 'approved' && (
                <div className="bg-green-50 border border-green-200 p-3 rounded-lg">
                  <p className="text-sm text-green-800">
                    <strong>Note:</strong> Approving this request will immediately change
                    the company's plan to {selectedRequest.requested_plan?.display_name}.
                  </p>
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  onClick={handleReview}
                  className="flex-1"
                  variant={reviewAction === 'approved' ? 'default' : 'destructive'}
                >
                  {reviewAction === 'approved' ? 'Approve' : 'Reject'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowReviewModal(false);
                    setSelectedRequest(null);
                    setReviewMessage('');
                  }}
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

export default function PlanRequestsAdminPage() {
  return (
    <ProtectedRoute allowedRoles={['system_admin']}>
      <AppLayout>
        <PlanRequestsAdminContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
