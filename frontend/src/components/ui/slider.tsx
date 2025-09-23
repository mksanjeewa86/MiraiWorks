import React, { forwardRef, useState, useRef, useEffect } from 'react';
import { clsx } from 'clsx';

interface SliderProps {
  value?: number[];
  defaultValue?: number[];
  onValueChange?: (value: number[]) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}

const Slider = forwardRef<HTMLDivElement, SliderProps>(
  (
    {
      value,
      defaultValue = [0],
      onValueChange,
      min = 0,
      max = 100,
      step = 1,
      disabled = false,
      className,
      orientation = 'horizontal',
      ...props
    },
    ref
  ) => {
    const [internalValue, setInternalValue] = useState(value || defaultValue);
    const sliderRef = useRef<HTMLDivElement>(null);
    const [isDragging, setIsDragging] = useState(false);

    const currentValue = value !== undefined ? value : internalValue;

    useEffect(() => {
      if (value !== undefined) {
        setInternalValue(value);
      }
    }, [value]);

    const handleValueChange = (newValue: number[]) => {
      if (value === undefined) {
        setInternalValue(newValue);
      }
      onValueChange?.(newValue);
    };

    const getPercentage = (val: number) => {
      return ((val - min) / (max - min)) * 100;
    };

    const getValueFromEvent = (event: React.MouseEvent | MouseEvent) => {
      if (!sliderRef.current) return currentValue[0];

      const rect = sliderRef.current.getBoundingClientRect();
      const isHorizontal = orientation === 'horizontal';

      const percentage = isHorizontal
        ? (event.clientX - rect.left) / rect.width
        : 1 - (event.clientY - rect.top) / rect.height;

      const newValue = min + percentage * (max - min);
      const steppedValue = Math.round(newValue / step) * step;
      return Math.max(min, Math.min(max, steppedValue));
    };

    const handleMouseDown = (event: React.MouseEvent) => {
      if (disabled) return;

      event.preventDefault();
      setIsDragging(true);

      const newValue = getValueFromEvent(event);
      handleValueChange([newValue]);

      const handleMouseMove = (moveEvent: MouseEvent) => {
        const newValue = getValueFromEvent(moveEvent);
        handleValueChange([newValue]);
      };

      const handleMouseUp = () => {
        setIsDragging(false);
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };

      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    };

    const handleKeyDown = (event: React.KeyboardEvent) => {
      if (disabled) return;

      let delta = 0;

      if (event.key === 'ArrowRight' || event.key === 'ArrowUp') {
        delta = step;
      } else if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') {
        delta = -step;
      } else if (event.key === 'Home') {
        delta = min - currentValue[0];
      } else if (event.key === 'End') {
        delta = max - currentValue[0];
      }

      if (delta !== 0) {
        event.preventDefault();
        const newValue = Math.max(min, Math.min(max, currentValue[0] + delta));
        handleValueChange([newValue]);
      }
    };

    const isHorizontal = orientation === 'horizontal';
    const percentage = getPercentage(currentValue[0]);

    return (
      <div
        ref={ref}
        className={clsx(
          'relative flex items-center select-none touch-none',
          isHorizontal ? 'w-full h-5' : 'h-full w-5 flex-col',
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
        {...props}
      >
        <div
          ref={sliderRef}
          className={clsx(
            'relative bg-gray-200 rounded-full',
            isHorizontal ? 'w-full h-2' : 'h-full w-2',
            !disabled && 'cursor-pointer'
          )}
          onMouseDown={handleMouseDown}
        >
          {/* Track filled */}
          <div
            className="absolute bg-blue-600 rounded-full"
            style={{
              [isHorizontal ? 'width' : 'height']: `${percentage}%`,
              [isHorizontal ? 'height' : 'width']: '100%',
            }}
          />

          {/* Thumb */}
          <div
            className={clsx(
              'absolute w-5 h-5 bg-white border-2 border-blue-600 rounded-full shadow-md',
              'transform -translate-x-1/2 -translate-y-1/2',
              !disabled && 'hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
              isDragging && 'shadow-lg'
            )}
            style={{
              [isHorizontal ? 'left' : 'top']: `${percentage}%`,
              [isHorizontal ? 'top' : 'left']: '50%',
            }}
            tabIndex={disabled ? -1 : 0}
            role="slider"
            aria-valuemin={min}
            aria-valuemax={max}
            aria-valuenow={currentValue[0]}
            aria-orientation={orientation}
            onKeyDown={handleKeyDown}
          />
        </div>
      </div>
    );
  }
);

Slider.displayName = 'Slider';

export { Slider };