// Type declarations for optional external modules

declare module 'face-api.js' {
  export interface FaceExpressions {
    happy: number;
    sad: number;
    angry: number;
    fearful: number;
    disgusted: number;
    surprised: number;
    neutral: number;
  }

  export interface FaceLandmarks {
    positions: any[];
  }

  export interface FaceDetection {
    expressions: FaceExpressions;
    landmarks: FaceLandmarks;
  }

  export class TinyFaceDetectorOptions {
    constructor(options?: any);
  }

  export const nets: {
    tinyFaceDetector: {
      loadFromUri(uri: string): Promise<void>;
    };
    faceExpressionNet: {
      loadFromUri(uri: string): Promise<void>;
    };
    faceLandmark68Net: {
      loadFromUri(uri: string): Promise<void>;
    };
  };

  export function detectAllFaces(
    input: HTMLVideoElement, 
    options: TinyFaceDetectorOptions
  ): {
    withFaceExpressions(): {
      withFaceLandmarks(): Promise<FaceDetection[]>;
    };
  };
}

declare module '@mediapipe/selfie_segmentation' {
  export interface SelfieSegmentationOptions {
    modelSelection: number;
    selfieMode: boolean;
  }

  export interface SelfieSegmentationResults {
    image: HTMLCanvasElement | HTMLVideoElement;
    segmentationMask: HTMLCanvasElement;
  }

  export class SelfieSegmentation {
    constructor(config: { locateFile: (file: string) => string });
    setOptions(options: SelfieSegmentationOptions): void;
    initialize(): Promise<void>;
    onResults(callback: (results: SelfieSegmentationResults) => void): void;
    send(input: { image: HTMLVideoElement }): void;
  }
}