"use client";

import { useMemo } from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import '@/styles/datepicker.css';
import clsx from 'clsx';

type DateTimePickerProps = {
  value?: string | null;
  onChange: (value: string | null) => void;
  label?: string;
  placeholder?: string;
  error?: string;
  helperText?: string;
  disabled?: boolean;
  required?: boolean;
  minuteStep?: number;
  id?: string;
  min?: string;
  max?: string;
  allowClear?: boolean;
  className?: string;
};

const OUTPUT_FORMAT = 'yyyy-MM-dd HH:mm';

function parseValue(input?: string | null): Date | null {
  if (!input) return null;
  const parsed = new Date(input);
  return isNaN(parsed.getTime()) ? null : parsed;
}

function formatDateTimeLocal(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

export default function DateTimePicker({
  value,
  onChange,
  label,
  placeholder,
  error,
  helperText,
  disabled,
  required,
  minuteStep = 15,
  id,
  min,
  max,
  allowClear = true,
  className,
}: DateTimePickerProps) {
  const selectedDate = useMemo(() => parseValue(value), [value]);
  const minDate = useMemo(() => parseValue(min), [min]);
  const maxDate = useMemo(() => parseValue(max), [max]);

  const handleChange = (date: Date | null) => {
    if (!date) {
      onChange(null);
      return;
    }

    onChange(formatDateTimeLocal(date));
  };

  const textFieldHelper = error ?? helperText ?? '';

  return (
    <div className={clsx('space-y-2', className)}>
      {label && (
        <label htmlFor={id} className={clsx('block text-sm font-medium', error ? 'text-red-700' : 'text-gray-700')}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        <DatePicker
          id={id}
          selected={selectedDate}
          onChange={handleChange}
          showTimeSelect
          timeFormat="HH:mm"
          timeIntervals={minuteStep}
          dateFormat="yyyy-MM-dd HH:mm"
          placeholderText={placeholder}
          disabled={disabled}
          minDate={minDate || undefined}
          maxDate={maxDate || undefined}
          isClearable={allowClear}
          className={clsx(
            'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            error ? 'border-red-300' : 'border-gray-300',
            disabled && 'opacity-50 cursor-not-allowed',
            'bg-white'
          )}
          wrapperClassName="w-full"
          popperClassName="z-50"
          calendarClassName="shadow-lg border border-gray-200 rounded-lg"
        />
      </div>
      {(error || helperText) && (
        <p className={clsx('mt-1 text-sm', error ? 'text-red-600' : 'text-gray-500')}>
          {textFieldHelper}
        </p>
      )}
    </div>
  );
}