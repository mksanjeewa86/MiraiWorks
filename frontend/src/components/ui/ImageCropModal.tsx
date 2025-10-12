'use client';

import { useState, useCallback, useEffect } from 'react';
import Cropper from 'react-easy-crop';
import { X } from 'lucide-react';
import { Button } from './button';

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
      <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-2xl w-full max-w-2xl mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            disabled={isCropping}
          >
            <X className="h-5 w-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Crop Area */}
        <div className="relative h-[400px] bg-gray-900 overflow-hidden">
          {!imageLoaded && imageSrc && (
            <div className="absolute inset-0 flex items-center justify-center text-white z-10 bg-gray-900">
              <p>Loading image...</p>
            </div>
          )}
          {imageError && (
            <div className="absolute inset-0 flex items-center justify-center text-red-400 z-10 bg-gray-900">
              <p>Failed to load image. Please try again.</p>
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
              <p>No image selected</p>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="p-4 space-y-4">
          {/* Zoom Slider */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Zoom
            </label>
            <input
              type="range"
              min={1}
              max={3}
              step={0.1}
              value={zoom}
              onChange={(e) => setZoom(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              disabled={isCropping}
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isCropping}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={isCropping}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isCropping ? 'Cropping...' : 'Save'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
