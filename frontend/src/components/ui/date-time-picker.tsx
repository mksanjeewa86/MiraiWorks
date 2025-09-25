"use client";

import { useMemo } from 'react';
import TextField from '@mui/material/TextField';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DateTimePicker as MuiDateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs, { Dayjs } from 'dayjs';
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

const OUTPUT_FORMAT = 'YYYY-MM-DDTHH:mm';

function parseValue(input?: string | null): Dayjs | null {
  if (!input) return null;
  const parsed = dayjs(input);
  return parsed.isValid() ? parsed : null;
}

function clampToBounds(value: Dayjs, minDate?: Dayjs | null, maxDate?: Dayjs | null): Dayjs {
  let next = value;
  if (minDate && next.isBefore(minDate)) {
    next = minDate;
  }
  if (maxDate && next.isAfter(maxDate)) {
    next = maxDate;
  }
  return next;
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

  const handleChange = (nextValue: Dayjs | null) => {
    if (!nextValue || !nextValue.isValid()) {
      onChange(null);
      return;
    }

    const adjusted = clampToBounds(nextValue, minDate, maxDate);
    onChange(adjusted.format(OUTPUT_FORMAT));
  };

  const textFieldHelper = error ?? helperText ?? '';

  return (
    <div className={clsx('space-y-2', className)}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <MuiDateTimePicker
          value={selectedDate}
          onChange={handleChange}
          disabled={disabled}
          minutesStep={minuteStep}
          minDateTime={minDate ?? undefined}
          maxDateTime={maxDate ?? undefined}
          format={OUTPUT_FORMAT}
          slotProps={{
            actionBar: { actions: allowClear ? ['clear', 'cancel', 'accept'] : ['cancel', 'accept'] },
            field: { clearable: allowClear },
            textField: {
              id,
              label,
              placeholder,
              required,
              fullWidth: true,
              size: 'small',
              error: Boolean(error),
              helperText: textFieldHelper ?? undefined,
            },
          }}
          slots={{
            textField: TextField,
          }}
        />
      </LocalizationProvider>
    </div>
  );
}
