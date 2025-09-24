'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  order_index: number;
  points: number;
  time_limit_seconds: number | null;
  is_required: boolean;
  options: Record<string, string> | null;
  max_length: number | null;
  min_length: number | null;
  rating_scale: number | null;
}

interface Answer {
  question_id: number;
  answer_data?: Record<string, any>;
  answer_text?: string;
  selected_options?: string[];
  time_spent_seconds?: number;
}

interface ExamQuestionProps {
  question: Question;
  answer?: Answer;
  onAnswerChange: (answer: Partial<Answer>) => void;
}

const QuestionType = {
  MULTIPLE_CHOICE: 'multiple_choice',
  SINGLE_CHOICE: 'single_choice',
  TEXT_INPUT: 'text_input',
  ESSAY: 'essay',
  TRUE_FALSE: 'true_false',
  RATING: 'rating',
  MATCHING: 'matching',
} as const;

export function ExamQuestion({ question, answer, onAnswerChange }: ExamQuestionProps) {
  const [selectedOptions, setSelectedOptions] = useState<string[]>(answer?.selected_options || []);
  const [textAnswer, setTextAnswer] = useState(answer?.answer_text || '');
  const [ratingValue, setRatingValue] = useState<number[]>(
    answer?.answer_data?.rating ? [answer.answer_data.rating] : [1]
  );

  useEffect(() => {
    setSelectedOptions(answer?.selected_options || []);
    setTextAnswer(answer?.answer_text || '');
    if (answer?.answer_data?.rating) {
      setRatingValue([answer.answer_data.rating]);
    }
  }, [question.id, answer]);

  const handleSingleChoice = (value: string) => {
    const newSelection = [value];
    setSelectedOptions(newSelection);
    onAnswerChange({
      selected_options: newSelection,
    });
  };

  const handleMultipleChoice = (option: string, checked: boolean) => {
    const newSelection = checked
      ? [...selectedOptions, option]
      : selectedOptions.filter((opt) => opt !== option);

    setSelectedOptions(newSelection);
    onAnswerChange({
      selected_options: newSelection,
    });
  };

  const handleTextChange = (value: string) => {
    setTextAnswer(value);
    onAnswerChange({
      answer_text: value,
    });
  };

  const handleRatingChange = (value: number[]) => {
    setRatingValue(value);
    onAnswerChange({
      answer_data: { rating: value[0] },
    });
  };

  const renderQuestionContent = () => {
    switch (question.question_type) {
      case QuestionType.SINGLE_CHOICE:
      case QuestionType.TRUE_FALSE:
        return (
          <RadioGroup
            value={selectedOptions[0] || ''}
            onValueChange={handleSingleChoice}
            className="space-y-3"
          >
            {question.options &&
              Object.entries(question.options).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2">
                  <RadioGroupItem value={key} id={`option-${key}`} />
                  <Label
                    htmlFor={`option-${key}`}
                    className="flex-1 cursor-pointer p-3 rounded-lg border border-gray-200 hover:bg-gray-50"
                  >
                    {value}
                  </Label>
                </div>
              ))}
          </RadioGroup>
        );

      case QuestionType.MULTIPLE_CHOICE:
        return (
          <div className="space-y-3">
            {question.options &&
              Object.entries(question.options).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2">
                  <Checkbox
                    id={`option-${key}`}
                    checked={selectedOptions.includes(key)}
                    onCheckedChange={(checked) => handleMultipleChoice(key, !!checked)}
                  />
                  <Label
                    htmlFor={`option-${key}`}
                    className="flex-1 cursor-pointer p-3 rounded-lg border border-gray-200 hover:bg-gray-50"
                  >
                    {value}
                  </Label>
                </div>
              ))}
          </div>
        );

      case QuestionType.TEXT_INPUT:
        return (
          <div className="space-y-2">
            <Textarea
              value={textAnswer}
              onChange={(e) => handleTextChange(e.target.value)}
              placeholder="Enter your answer..."
              maxLength={question.max_length || undefined}
              className="min-h-[100px]"
            />
            <div className="flex justify-between text-sm text-gray-500">
              {question.min_length && <span>Minimum {question.min_length} characters</span>}
              {question.max_length && (
                <span>
                  {textAnswer.length} / {question.max_length}
                </span>
              )}
            </div>
          </div>
        );

      case QuestionType.ESSAY:
        return (
          <div className="space-y-2">
            <Textarea
              value={textAnswer}
              onChange={(e) => handleTextChange(e.target.value)}
              placeholder="Write your essay here..."
              maxLength={question.max_length || undefined}
              className="min-h-[200px]"
            />
            <div className="flex justify-between text-sm text-gray-500">
              {question.min_length && <span>Minimum {question.min_length} characters</span>}
              {question.max_length && (
                <span>
                  {textAnswer.length} / {question.max_length}
                </span>
              )}
            </div>
          </div>
        );

      case QuestionType.RATING:
        const scale = question.rating_scale || 5;
        return (
          <div className="space-y-4">
            <div className="px-4">
              <Slider
                value={ratingValue}
                onValueChange={handleRatingChange}
                min={1}
                max={scale}
                step={1}
                className="w-full"
              />
            </div>
            <div className="flex justify-between text-sm text-gray-600">
              <span>1 (Lowest)</span>
              <span className="font-medium">
                Selected: {ratingValue[0]} / {scale}
              </span>
              <span>{scale} (Highest)</span>
            </div>
          </div>
        );

      case QuestionType.MATCHING:
        // For matching questions, you would need a more complex interface
        // This is a simplified version
        return (
          <div className="text-center py-8 text-gray-500">
            <p>Matching questions are not yet implemented in this demo.</p>
          </div>
        );

      default:
        return (
          <div className="text-center py-8 text-gray-500">
            <p>Unknown question type: {question.question_type}</p>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Question Text */}
      <div className="prose prose-gray max-w-none">
        <div className="text-lg font-medium text-gray-900 leading-relaxed whitespace-pre-wrap">
          {question.question_text}
        </div>
      </div>

      {/* Answer Area */}
      <div className="bg-gray-50 p-6 rounded-lg">{renderQuestionContent()}</div>

      {/* Question Info */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-4">
          {question.is_required && <span className="text-red-600 font-medium">* Required</span>}
          {question.time_limit_seconds && (
            <span>Time limit: {Math.floor(question.time_limit_seconds / 60)} minutes</span>
          )}
        </div>
        <div>
          {question.points} {question.points === 1 ? 'point' : 'points'}
        </div>
      </div>
    </div>
  );
}
