'use client';

import React, { Component, ReactNode, ErrorInfo } from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

/**
 * Global Error Boundary Component
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by boundary:', {
        error: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
      });
    }

    // In production, you would send this to an error reporting service
    // Example: Sentry, LogRocket, etc.
    // this.logErrorToService(error, errorInfo);

    // Store error info in state for display
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-screen flex items-center justify-center px-4 bg-gray-50 dark:bg-gray-900">
          <div className="max-w-md w-full">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
              {/* Error Icon */}
              <div className="flex justify-center mb-6">
                <div className="rounded-full bg-red-100 dark:bg-red-900/20 p-4">
                  <AlertCircle className="h-12 w-12 text-red-600 dark:text-red-400" />
                </div>
              </div>

              {/* Error Title */}
              <h1 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-2">
                Oops! Something went wrong
              </h1>

              {/* Error Description */}
              <p className="text-center text-gray-600 dark:text-gray-400 mb-6">
                We're sorry for the inconvenience. An unexpected error occurred.
              </p>

              {/* Error Details (Development Only) */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="mb-6">
                  <details className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                    <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Error Details
                    </summary>
                    <div className="mt-2 text-xs font-mono text-gray-600 dark:text-gray-400 overflow-auto max-h-48">
                      <p className="font-semibold text-red-600 dark:text-red-400 mb-2">
                        {this.state.error.message}
                      </p>
                      <pre className="whitespace-pre-wrap break-words">
                        {this.state.error.stack}
                      </pre>
                      {this.state.errorInfo?.componentStack && (
                        <pre className="whitespace-pre-wrap break-words mt-4">
                          Component Stack:
                          {this.state.errorInfo.componentStack}
                        </pre>
                      )}
                    </div>
                  </details>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={this.handleReset}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <RefreshCw className="h-4 w-4" />
                  Try Again
                </button>
                <button
                  onClick={this.handleGoHome}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  <Home className="h-4 w-4" />
                  Go Home
                </button>
              </div>

              {/* Help Text */}
              <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
                If this problem persists, please{' '}
                <a
                  href="mailto:support@miraiworks.com"
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  contact support
                </a>
                .
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Hook-based error boundary wrapper
 * Use this for functional components that need error boundaries
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode
): React.FC<P> {
  return function WithErrorBoundaryWrapper(props: P) {
    return (
      <ErrorBoundary fallback={fallback}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
}

/**
 * Example usage:
 *
 * // Wrap your entire app
 * <ErrorBoundary>
 *   <App />
 * </ErrorBoundary>
 *
 * // Wrap specific components
 * <ErrorBoundary fallback={<CustomErrorUI />}>
 *   <RiskyComponent />
 * </ErrorBoundary>
 *
 * // Use with functional components
 * export default withErrorBoundary(MyComponent);
 */

export default ErrorBoundary;
