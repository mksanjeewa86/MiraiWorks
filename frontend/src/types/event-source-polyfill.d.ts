declare module 'event-source-polyfill' {
  interface EventSourcePolyfillInit extends EventSourceInit {
    headers?: Record<string, string>;
  }

  export class EventSourcePolyfill extends EventSource {
    constructor(url: string | URL, eventSourceInitDict?: EventSourcePolyfillInit);
  }

  export const NativeEventSource: typeof EventSource;
}
