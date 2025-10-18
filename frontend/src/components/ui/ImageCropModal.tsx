'use client';

import { useState, useCallback, useEffect } from 'react';
import Cropper from 'react-easy-crop';
import { X, Crop } from 'lucide-react';
import { Button } from './Button';

interface ImageCropModalProps {
  isOpen: boolean;
  imageSrc: string;
  onClose: () => void;
  onCropComplete: (croppedImageBlob: Blob, croppedImageUrl: string) => void;
  aspect?: number; // Aspect ratio (e.g., 1 for square, 16/9 for cover)
  cropShape?: 'rect' | 'round'; // Shape of crop area
  title?: string; // Modal title
}

interface CropArea {
  x: number;
  y: number;
  width: number;
  height: number;
}

export default function ImageCropModal({
  isOpen,
  imageSrc,
  onClose,
  onCropComplete,
  aspect = 1,
  cropShape = 'round',
  title = 'Crop Profile Photo',
}: ImageCropModalProps) {
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<CropArea | null>(null);
  const [isCropping, setIsCropping] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  // Reset state when modal opens with new image
  useEffect(() => {
    if (isOpen && imageSrc) {
      setImageLoaded(false);
      setImageError(false);
      setCrop({ x: 0, y: 0 });
      setZoom(1);

      // Test if image can load in browser
      const testImg = new Image();
      testImg.onload = () => {
        setImageLoaded(true);
      };
      testImg.onerror = (e) => {
        console.error('Test image failed to load:', e);
        setImageError(true);
      };
      testImg.src = imageSrc;
    }
  }, [isOpen, imageSrc]);

  const onCropChange = (location: { x: number; y: number }) => {
    setCrop(location);
  };

  const onZoomChange = (zoom: number) => {
    setZoom(zoom);
  };

  const onCropCompleteInternal = useCallback(
    (croppedArea: CropArea, croppedAreaPixels: CropArea) => {
      setCroppedAreaPixels(croppedAreaPixels);
    },
    []
  );

  const createCroppedImage = async (): Promise<{ blob: Blob; url: string }> => {
    if (!croppedAreaPixels) {
      throw new Error('No crop area defined');
    }

    const image = new Image();
    image.src = imageSrc;

    return new Promise((resolve, reject) => {
      image.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        if (!ctx) {
          reject(new Error('Failed to get canvas context'));
          return;
        }

        // Set canvas size to crop area
        canvas.width = croppedAreaPixels.width;
        canvas.height = croppedAreaPixels.height;

        // Draw cropped image
        ctx.drawImage(
          image,
          croppedAreaPixels.x,
          croppedAreaPixels.y,
          croppedAreaPixels.width,
          croppedAreaPixels.height,
          0,
          0,
          croppedAreaPixels.width,
          croppedAreaPixels.height
        );

        // Convert to blob
        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error('Failed to create blob'));
              return;
            }

            const url = URL.createObjectURL(blob);
            resolve({ blob, url });
          },
          'image/jpeg',
          0.95
        );
      };

      image.onerror = () => {
        reject(new Error('Failed to load image'));
      };
    });
  };

  const handleSave = async () => {
    if (!croppedAreaPixels) return;

    setIsCropping(true);
    try {
      const { blob, url } = await createCroppedImage();
      onCropComplete(blob, url);
      onClose();
    } catch (error) {
      console.error('Error cropping image:', error);
      alert('Failed to crop image. Please try again.');
    } finally {
      setIsCropping(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative bg-white rounded-3xl border border-slate-200 shadow-[0_30px_80px_-20px_rgba(15,23,42,0.2)] w-full max-w-3xl mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 px-6 pt-6 pb-4">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600">
              <Crop className="h-5 w-5" />
            </span>
            <div>
              <h3 className="text-xl font-semibold text-slate-900">
                {title}
              </h3>
              <p className="text-sm text-slate-500">
                Adjust the crop area and zoom to fit your image perfectly
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
            disabled={isCropping}
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Crop Area */}
        <div className="relative h-[450px] bg-slate-900 overflow-hidden mx-6 rounded-2xl border border-slate-200">
          {!imageLoaded && imageSrc && (
            <div className="absolute inset-0 flex items-center justify-center text-white z-10 bg-slate-900">
              <p className="text-sm">Loading image...</p>
            </div>
          )}
          {imageError && (
            <div className="absolute inset-0 flex items-center justify-center text-red-400 z-10 bg-slate-900">
              <p className="text-sm">Failed to load image. Please try again.</p>
            </div>
          )}
          {imageSrc && !imageError && (
            <Cropper
              image={imageSrc}
              crop={crop}
              zoom={zoom}
              aspect={aspect}
              cropShape={cropShape}
              showGrid={false}
              onCropChange={onCropChange}
              onZoomChange={onZoomChange}
              onCropComplete={onCropCompleteInternal}
            />
          )}
          {!imageSrc && (
            <div className="flex items-center justify-center h-full text-white">
              <p className="text-sm">No image selected</p>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="px-6 py-4 space-y-6">
          {/* Zoom Slider */}
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
            <label className="block text-sm font-medium text-slate-700 mb-3">
              Zoom Level
            </label>
            <input
              type="range"
              min={1}
              max={3}
              step={0.1}
              value={zoom}
              onChange={(e) => setZoom(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              disabled={isCropping}
            />
            <div className="flex justify-between mt-2">
              <span className="text-xs text-slate-500">1x</span>
              <span className="text-xs text-slate-500">3x</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex-shrink-0 gap-3 border-t border-slate-200 bg-white px-6 py-4 flex justify-end">
          <Button
            variant="ghost"
            onClick={onClose}
            disabled={isCropping}
            className="min-w-[120px] border border-slate-300 bg-white text-slate-600 hover:bg-slate-100"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={isCropping}
            className="min-w-[160px] bg-blue-600 text-white shadow-lg shadow-blue-500/30 hover:bg-blue-600/90"
          >
            {isCropping ? 'Cropping...' : 'Save Image'}
          </Button>
        </div>
      </div>
    </div>
  );
}
