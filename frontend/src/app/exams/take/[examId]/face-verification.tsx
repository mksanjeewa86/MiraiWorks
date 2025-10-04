'use client';

import { useState, useRef, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui';
import { Button } from '@/components/ui';
import { Camera, AlertTriangle } from 'lucide-react';
import { LoadingSpinner } from '@/components/ui';
import { toast } from 'sonner';
import { API_ENDPOINTS } from '@/api/config';
import type { FaceVerificationProps } from '@/types/components';

export function FaceVerification({ sessionId, onComplete }: FaceVerificationProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturing, setCapturing] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user',
        },
      });

      setStream(mediaStream);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      setPermissionDenied(true);
      toast.error('Camera access is required for face verification');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
  };

  const captureAndVerify = async () => {
    if (!videoRef.current || !canvasRef.current || !stream) {
      toast.error('Camera not ready');
      return;
    }

    setCapturing(true);
    setVerifying(true);

    try {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      const context = canvas.getContext('2d');

      if (!context) {
        throw new Error('Canvas context not available');
      }

      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Capture frame
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert to base64
      const imageData = canvas.toDataURL('image/jpeg', 0.8);

      // Submit for verification
      const response = await fetch(API_ENDPOINTS.EXAM_SESSIONS.FACE_VERIFICATION(sessionId), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          session_id: sessionId,
          image_data: imageData.split(',')[1], // Remove data:image/jpeg;base64, prefix
          timestamp: new Date().toISOString(),
          verification_type: 'periodic',
        }),
      });

      if (!response.ok) {
        throw new Error('Verification request failed');
      }

      const result = await response.json();

      if (result.verified) {
        toast.success('Face verification successful');
        setIsOpen(false);
        onComplete(true);
      } else {
        toast.error(result.message || 'Face verification failed');
        if (result.requires_human_review) {
          toast.info('Your verification will be reviewed manually');
        }
        onComplete(false);
      }
    } catch (error) {
      console.error('Error during face verification:', error);
      toast.error('Face verification failed');
      onComplete(false);
    } finally {
      setCapturing(false);
      setVerifying(false);
      stopCamera();
    }
  };

  const skipVerification = () => {
    toast.warning('Face verification skipped - this has been recorded');
    setIsOpen(false);
    onComplete(false);
    stopCamera();
  };

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-[500px]" closeButton={false}>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            Face Verification Required
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="text-sm text-gray-600">
            Please capture a clear photo of your face for identity verification. Make sure you are
            in a well-lit area and looking directly at the camera.
          </div>

          {permissionDenied ? (
            <div className="text-center py-8">
              <AlertTriangle className="h-12 w-12 mx-auto text-red-500 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Camera Access Required</h3>
              <p className="text-gray-600 mb-4">
                Please allow camera access to continue with face verification.
              </p>
              <Button onClick={startCamera} variant="outline">
                Retry Camera Access
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Camera View */}
              <div className="relative bg-black rounded-lg overflow-hidden">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-64 object-cover"
                />

                {/* Overlay guide */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="w-48 h-60 border-2 border-white rounded-full opacity-50" />
                </div>

                {capturing && (
                  <div className="absolute inset-0 bg-white opacity-30 animate-pulse" />
                )}
              </div>

              {/* Hidden canvas for capturing */}
              <canvas ref={canvasRef} className="hidden" />

              {/* Verification Status */}
              {verifying && (
                <div className="flex items-center justify-center gap-2 py-4">
                  <LoadingSpinner size="sm" />
                  <span className="text-sm text-gray-600">Verifying face...</span>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 justify-center">
                <Button
                  onClick={captureAndVerify}
                  disabled={!stream || capturing || verifying}
                  className="flex-1"
                >
                  {verifying ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Verifying...
                    </>
                  ) : (
                    <>
                      <Camera className="h-4 w-4 mr-2" />
                      Capture & Verify
                    </>
                  )}
                </Button>

                <Button onClick={skipVerification} variant="outline" disabled={verifying}>
                  Skip
                </Button>
              </div>

              <div className="text-xs text-gray-500 text-center">
                Your photo is used only for identity verification and is not stored permanently.
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
