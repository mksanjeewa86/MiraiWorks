import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock WebRTC APIs
const mockRTCPeerConnection = vi.fn().mockImplementation(() => ({
  createOffer: vi.fn().mockResolvedValue({}),
  createAnswer: vi.fn().mockResolvedValue({}),
  setLocalDescription: vi.fn().mockResolvedValue(undefined),
  setRemoteDescription: vi.fn().mockResolvedValue(undefined),
  addIceCandidate: vi.fn().mockResolvedValue(undefined),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  close: vi.fn(),
  getStats: vi.fn().mockResolvedValue([]),
  iceConnectionState: 'new',
  connectionState: 'new',
  signalingState: 'stable'
}));

const mockMediaDevices = {
  getUserMedia: vi.fn().mockResolvedValue({
    getTracks: vi.fn().mockReturnValue([
      { stop: vi.fn(), kind: 'video' },
      { stop: vi.fn(), kind: 'audio' }
    ])
  }),
  getDisplayMedia: vi.fn().mockResolvedValue({
    getTracks: vi.fn().mockReturnValue([
      { stop: vi.fn(), kind: 'video' }
    ])
  }),
  enumerateDevices: vi.fn().mockResolvedValue([])
};

// Mock HTMLMediaElement methods
Object.defineProperty(HTMLMediaElement.prototype, 'play', {
  writable: true,
  value: vi.fn().mockResolvedValue(undefined),
});

Object.defineProperty(HTMLMediaElement.prototype, 'pause', {
  writable: true,
  value: vi.fn(),
});

// Mock Canvas API for virtual background
const mockCanvasContext = {
  drawImage: vi.fn(),
  getImageData: vi.fn().mockReturnValue({
    data: new Uint8ClampedArray(4),
    width: 1,
    height: 1
  }),
  putImageData: vi.fn(),
  fillRect: vi.fn(),
  clearRect: vi.fn(),
  save: vi.fn(),
  restore: vi.fn(),
  scale: vi.fn(),
  translate: vi.fn(),
  filter: 'none'
};

HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue(mockCanvasContext);
HTMLCanvasElement.prototype.captureStream = vi.fn().mockReturnValue({
  getTracks: vi.fn().mockReturnValue([])
});

// Mock Socket.IO
vi.mock('socket.io-client', () => ({
  io: vi.fn(() => ({
    emit: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    connect: vi.fn(),
    disconnect: vi.fn(),
    connected: false
  }))
}));

// Mock face-api.js
vi.mock('face-api.js', () => ({
  nets: {
    tinyFaceDetector: {
      loadFromUri: vi.fn().mockResolvedValue(undefined)
    },
    faceExpressionNet: {
      loadFromUri: vi.fn().mockResolvedValue(undefined)
    },
    faceLandmark68Net: {
      loadFromUri: vi.fn().mockResolvedValue(undefined)
    }
  },
  TinyFaceDetectorOptions: vi.fn(),
  detectAllFaces: vi.fn().mockReturnValue({
    withFaceExpressions: vi.fn().mockReturnValue({
      withFaceLandmarks: vi.fn().mockResolvedValue([])
    })
  })
}));

// Mock MediaPipe
vi.mock('@mediapipe/selfie_segmentation', () => ({
  SelfieSegmentation: vi.fn().mockImplementation(() => ({
    setOptions: vi.fn(),
    initialize: vi.fn().mockResolvedValue(undefined),
    onResults: vi.fn(),
    send: vi.fn()
  }))
}));

// Global mocks
Object.defineProperty(window, 'RTCPeerConnection', {
  writable: true,
  value: mockRTCPeerConnection,
});

Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: mockMediaDevices,
});

// Mock window.confirm for expression analysis consent
Object.defineProperty(window, 'confirm', {
  writable: true,
  value: vi.fn().mockReturnValue(true),
});

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock requestAnimationFrame
global.requestAnimationFrame = vi.fn((cb: FrameRequestCallback) => setTimeout(cb as any, 16) as any);
global.cancelAnimationFrame = vi.fn((id: number) => clearTimeout(id as any));

// Suppress console warnings in tests
global.console = {
  ...console,
  warn: vi.fn(),
  error: vi.fn(),
};