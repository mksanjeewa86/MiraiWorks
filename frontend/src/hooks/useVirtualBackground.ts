import { useState, useRef, useCallback, useEffect } from 'react';

interface VirtualBackgroundOptions {
  type: 'none' | 'blur' | 'image' | 'video';
  source?: string;
  blurAmount?: number;
}

interface VirtualBackgroundState {
  isSupported: boolean;
  isEnabled: boolean;
  isProcessing: boolean;
  currentBackground: VirtualBackgroundOptions;
  availableBackgrounds: VirtualBackgroundOptions[];
  error?: string;
}

export const useVirtualBackground = (videoStream?: MediaStream) => {
  const [state, setState] = useState<VirtualBackgroundState>({
    isSupported: false,
    isEnabled: false,
    isProcessing: false,
    currentBackground: { type: 'none' },
    availableBackgrounds: [
      { type: 'none' },
      { type: 'blur', blurAmount: 10 },
      { type: 'blur', blurAmount: 20 },
      { type: 'image', source: '/backgrounds/office.jpg' },
      { type: 'image', source: '/backgrounds/home.jpg' },
      { type: 'image', source: '/backgrounds/nature.jpg' },
      { type: 'image', source: '/backgrounds/abstract.jpg' }
    ]
  });

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const backgroundImageRef = useRef<HTMLImageElement | null>(null);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const modelRef = useRef<any>(null);

  // Check if virtual background is supported
  const checkSupport = useCallback(() => {
    try {
      // Check if the browser supports OffscreenCanvas and WebAssembly
      const hasOffscreenCanvas = 'OffscreenCanvas' in window;
      const hasWebAssembly = 'WebAssembly' in window;
      const hasWebGL = !!document.createElement('canvas').getContext('webgl2');
      
      const supported = hasOffscreenCanvas && hasWebAssembly && hasWebGL;
      
      setState(prev => ({
        ...prev,
        isSupported: supported
      }));

      return supported;
    } catch (error) {
      console.error('Error checking virtual background support:', error);
      setState(prev => ({
        ...prev,
        isSupported: false,
        error: 'Failed to check browser support'
      }));
      return false;
    }
  }, []);

  // Load MediaPipe Selfie Segmentation model
  const loadSegmentationModel = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, isProcessing: true }));

      // Dynamically import MediaPipe selfie segmentation (optional dependency)
      const { SelfieSegmentation } = await import('@mediapipe/selfie_segmentation').catch(() => {
        throw new Error('MediaPipe Selfie Segmentation is not available. Please install it with: npm install @mediapipe/selfie_segmentation');
      });
      
      const selfieSegmentation = new SelfieSegmentation({
        locateFile: (file: string) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/${file}`;
        }
      });

      selfieSegmentation.setOptions({
        modelSelection: 1, // 0 for general, 1 for landscape (better quality)
        selfieMode: true,
      });

      await new Promise<void>((resolve, reject) => {
        selfieSegmentation.onResults(() => {
          // Results handler will be set up later
        });

        selfieSegmentation.initialize().then(() => resolve()).catch(reject);
      });

      modelRef.current = selfieSegmentation;
      setState(prev => ({ ...prev, isProcessing: false }));
      
      return selfieSegmentation;
    } catch (error) {
      console.error('Error loading segmentation model:', error);
      setState(prev => ({
        ...prev,
        isProcessing: false,
        error: 'Failed to load background processing model'
      }));
      throw error;
    }
  }, []);

  // Apply virtual background to video frame
  const processFrame = useCallback(() => {
    if (!canvasRef.current || !videoRef.current || !state.isEnabled) {
      return;
    }

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx) return;

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    if (state.currentBackground.type === 'none') {
      // No background processing, just draw the video
      ctx.drawImage(video, 0, 0);
    } else if (state.currentBackground.type === 'blur') {
      // Apply blur effect
      ctx.filter = `blur(${state.currentBackground.blurAmount || 10}px)`;
      ctx.drawImage(video, 0, 0);
      ctx.filter = 'none';
    } else if (modelRef.current && state.currentBackground.type === 'image') {
      // Use MediaPipe for background replacement
      modelRef.current.send({ image: video });
    }

    // Continue processing frames
    if (state.isEnabled) {
      animationFrameRef.current = requestAnimationFrame(processFrame);
    }
  }, [state.isEnabled, state.currentBackground]);

  // Handle segmentation results from MediaPipe
  const handleSegmentationResults = useCallback((results: any) => {
    if (!canvasRef.current || !backgroundImageRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { image, segmentationMask } = results;

    // Draw background image
    ctx.drawImage(backgroundImageRef.current, 0, 0, canvas.width, canvas.height);

    // Create a temporary canvas for compositing
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;
    const tempCtx = tempCanvas.getContext('2d');

    if (!tempCtx) return;

    // Draw the person (foreground) using the segmentation mask
    tempCtx.globalCompositeOperation = 'source-over';
    tempCtx.drawImage(image, 0, 0);

    // Use segmentation mask to blend
    tempCtx.globalCompositeOperation = 'destination-in';
    tempCtx.drawImage(segmentationMask, 0, 0);

    // Draw the masked person onto the main canvas
    ctx.globalCompositeOperation = 'source-over';
    ctx.drawImage(tempCanvas, 0, 0);
  }, []);

  // Set up MediaPipe results callback
  useEffect(() => {
    if (modelRef.current) {
      modelRef.current.onResults(handleSegmentationResults);
    }
  }, [handleSegmentationResults]);

  // Load background image
  const loadBackgroundImage = useCallback(async (imageSrc: string) => {
    return new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => {
        backgroundImageRef.current = img;
        resolve(img);
      };
      
      img.onerror = () => {
        reject(new Error(`Failed to load background image: ${imageSrc}`));
      };
      
      img.src = imageSrc;
    });
  }, []);

  // Enable virtual background
  const enableBackground = useCallback(async (background: VirtualBackgroundOptions) => {
    try {
      setState(prev => ({ ...prev, isProcessing: true, error: undefined }));

      // Load background image if needed
      if (background.type === 'image' && background.source) {
        await loadBackgroundImage(background.source);
      }

      // Load segmentation model if not already loaded and needed
      if (!modelRef.current && background.type === 'image') {
        await loadSegmentationModel();
      }

      setState(prev => ({
        ...prev,
        isEnabled: true,
        isProcessing: false,
        currentBackground: background
      }));

      // Start processing frames
      if (background.type !== 'none') {
        processFrame();
      }

    } catch (error) {
      console.error('Error enabling virtual background:', error);
      setState(prev => ({
        ...prev,
        isProcessing: false,
        error: error instanceof Error ? error.message : 'Failed to enable virtual background'
      }));
    }
  }, [loadBackgroundImage, loadSegmentationModel, processFrame]);

  // Disable virtual background
  const disableBackground = useCallback(() => {
    setState(prev => ({
      ...prev,
      isEnabled: false,
      currentBackground: { type: 'none' }
    }));

    // Cancel animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  }, []);

  // Get processed video stream
  const getProcessedStream = useCallback((): MediaStream | null => {
    if (!canvasRef.current || !state.isEnabled) {
      return videoStream || null;
    }

    try {
      return canvasRef.current.captureStream(30); // 30 FPS
    } catch (error) {
      console.error('Error capturing processed stream:', error);
      return videoStream || null;
    }
  }, [videoStream, state.isEnabled]);

  // Upload custom background
  const uploadCustomBackground = useCallback(async (file: File): Promise<VirtualBackgroundOptions> => {
    return new Promise((resolve, reject) => {
      if (!file.type.startsWith('image/')) {
        reject(new Error('Please select a valid image file'));
        return;
      }

      const reader = new FileReader();
      
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string;
        const customBackground: VirtualBackgroundOptions = {
          type: 'image',
          source: dataUrl
        };

        setState(prev => ({
          ...prev,
          availableBackgrounds: [...prev.availableBackgrounds, customBackground]
        }));

        resolve(customBackground);
      };

      reader.onerror = () => {
        reject(new Error('Failed to read image file'));
      };

      reader.readAsDataURL(file);
    });
  }, []);

  // Initialize on mount
  useEffect(() => {
    checkSupport();
  }, [checkSupport]);

  // Set up canvas and video references
  useEffect(() => {
    if (!canvasRef.current) {
      canvasRef.current = document.createElement('canvas');
    }

    if (!videoRef.current && videoStream) {
      videoRef.current = document.createElement('video');
      videoRef.current.srcObject = videoStream;
      videoRef.current.autoplay = true;
      videoRef.current.muted = true;
      videoRef.current.playsInline = true;
    }
  }, [videoStream]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return {
    ...state,
    enableBackground,
    disableBackground,
    getProcessedStream,
    uploadCustomBackground,
    canvasRef,
    checkSupport
  };
};