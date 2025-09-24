'use client';

import { useEffect, useRef } from 'react';
import { toast } from 'sonner';

interface WebUsageMonitorProps {
  onWebUsageDetected: (eventType: string, eventData: any) => void;
  allowWebUsage: boolean;
}

export function WebUsageMonitor({ onWebUsageDetected, allowWebUsage }: WebUsageMonitorProps) {
  const lastFocusTime = useRef<number>(Date.now());
  const isPageVisible = useRef<boolean>(true);

  useEffect(() => {
    let warningShown = false;

    // Handle tab/window focus changes
    const handleVisibilityChange = () => {
      const now = Date.now();
      const isVisible = !document.hidden;

      if (!isVisible && isPageVisible.current) {
        // Tab became hidden
        lastFocusTime.current = now;
        isPageVisible.current = false;

        if (!allowWebUsage && !warningShown) {
          toast.warning('Tab switching detected and recorded', {
            description: 'Please stay on this tab during the exam',
          });
          warningShown = true;
        }

        onWebUsageDetected('tab_switch', {
          action: 'tab_hidden',
          timestamp: new Date().toISOString(),
          previous_focus_duration: now - lastFocusTime.current,
        });
      } else if (isVisible && !isPageVisible.current) {
        // Tab became visible again
        const awayDuration = now - lastFocusTime.current;
        isPageVisible.current = true;
        lastFocusTime.current = now;

        onWebUsageDetected('tab_switch', {
          action: 'tab_visible',
          timestamp: new Date().toISOString(),
          away_duration: awayDuration,
        });

        if (awayDuration > 5000) {
          // Away for more than 5 seconds
          toast.warning(`You were away for ${Math.round(awayDuration / 1000)} seconds`, {
            description: 'This has been recorded for security purposes',
          });
        }
      }
    };

    // Handle window focus/blur
    const handleFocus = () => {
      if (!isPageVisible.current) {
        isPageVisible.current = true;
        lastFocusTime.current = Date.now();

        onWebUsageDetected('window_focus', {
          action: 'focus_gained',
          timestamp: new Date().toISOString(),
        });
      }
    };

    const handleBlur = () => {
      if (isPageVisible.current) {
        isPageVisible.current = false;

        onWebUsageDetected('window_focus', {
          action: 'focus_lost',
          timestamp: new Date().toISOString(),
        });

        if (!allowWebUsage) {
          toast.warning('Window focus lost - please stay focused on the exam');
        }
      }
    };

    // Handle right-click (context menu)
    const handleContextMenu = (e: MouseEvent) => {
      if (!allowWebUsage) {
        e.preventDefault();
        toast.warning('Right-click disabled during exam');

        onWebUsageDetected('context_menu', {
          timestamp: new Date().toISOString(),
          coordinates: { x: e.clientX, y: e.clientY },
        });
      }
    };

    // Handle key combinations (like Alt+Tab, Ctrl+T, etc.)
    const handleKeyDown = (e: KeyboardEvent) => {
      const suspiciousCombinations = [
        { key: 'Tab', alt: true }, // Alt+Tab
        { key: 'Tab', ctrl: true, shift: true }, // Ctrl+Shift+Tab
        { key: 't', ctrl: true }, // Ctrl+T (new tab)
        { key: 'n', ctrl: true }, // Ctrl+N (new window)
        { key: 'w', ctrl: true }, // Ctrl+W (close tab)
        { key: 'r', ctrl: true }, // Ctrl+R (refresh)
        { key: 'F5' }, // F5 (refresh)
        { key: 'F11' }, // F11 (fullscreen toggle)
        { key: 'F12' }, // F12 (dev tools)
      ];

      const isSuspicious = suspiciousCombinations.some((combo) => {
        return (
          e.key === combo.key &&
          (!combo.ctrl || e.ctrlKey) &&
          (!combo.alt || e.altKey) &&
          (!combo.shift || e.shiftKey)
        );
      });

      if (isSuspicious) {
        if (!allowWebUsage) {
          e.preventDefault();
          toast.warning('That key combination is disabled during the exam');
        }

        onWebUsageDetected('key_combination', {
          key: e.key,
          ctrl: e.ctrlKey,
          alt: e.altKey,
          shift: e.shiftKey,
          timestamp: new Date().toISOString(),
        });
      }

      // Log Escape key (might indicate attempt to exit fullscreen)
      if (e.key === 'Escape') {
        onWebUsageDetected('escape_key', {
          timestamp: new Date().toISOString(),
        });
      }
    };

    // Handle mouse leave (might indicate switching to another window)
    const handleMouseLeave = () => {
      onWebUsageDetected('mouse_leave', {
        timestamp: new Date().toISOString(),
      });
    };

    // Handle fullscreen changes
    const handleFullscreenChange = () => {
      const isFullscreen = !!document.fullscreenElement;

      onWebUsageDetected('fullscreen_change', {
        is_fullscreen: isFullscreen,
        timestamp: new Date().toISOString(),
      });

      if (!isFullscreen && !allowWebUsage) {
        toast.warning('Please stay in fullscreen mode during the exam');
      }
    };

    // Handle print attempts
    const handleBeforePrint = () => {
      onWebUsageDetected('print_attempt', {
        timestamp: new Date().toISOString(),
      });

      if (!allowWebUsage) {
        toast.warning('Printing is not allowed during the exam');
      }
    };

    // Handle copy/paste attempts
    const handleCopy = (e: ClipboardEvent) => {
      onWebUsageDetected('copy_attempt', {
        timestamp: new Date().toISOString(),
      });

      if (!allowWebUsage) {
        e.preventDefault();
        toast.warning('Copying is not allowed during the exam');
      }
    };

    const handlePaste = (e: ClipboardEvent) => {
      onWebUsageDetected('paste_attempt', {
        timestamp: new Date().toISOString(),
      });

      // You might want to allow pasting in text areas
      // but log it for monitoring purposes
    };

    // Add event listeners
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);
    window.addEventListener('blur', handleBlur);
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mouseleave', handleMouseLeave);
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    window.addEventListener('beforeprint', handleBeforePrint);
    document.addEventListener('copy', handleCopy);
    document.addEventListener('paste', handlePaste);

    // Cleanup
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('blur', handleBlur);
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mouseleave', handleMouseLeave);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      window.removeEventListener('beforeprint', handleBeforePrint);
      document.removeEventListener('copy', handleCopy);
      document.removeEventListener('paste', handlePaste);
    };
  }, [onWebUsageDetected, allowWebUsage]);

  // This component doesn't render anything visible
  return null;
}
