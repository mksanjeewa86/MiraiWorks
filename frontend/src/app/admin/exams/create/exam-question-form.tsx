'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Plus, Trash2, Save, X } from 'lucide-react';

interface QuestionFormData {
  question_text: string;
  question_type: string;
  points: number;
  time_limit_seconds: number | null;
  is_required: boolean;
  options: Record<string, string>;
  correct_answers: string[];
  max_length: number | null;
  min_length: number | null;
  rating_scale: number | null;
  explanation: string;
  tags: string[];
}

interface ExamQuestionFormProps {
  question: QuestionFormData;
  onSave: (question: QuestionFormData) => void;
  onCancel: () => void;
}

const QuestionType = {
  MULTIPLE_CHOICE: 'multiple_choice',
  SINGLE_CHOICE: 'single_choice',
  TEXT_INPUT: 'text_input',
  ESSAY: 'essay',
  TRUE_FALSE: 'true_false',
  RATING: 'rating',
} as const;

export function ExamQuestionForm({ question, onSave, onCancel }: ExamQuestionFormProps) {
  const [formData, setFormData] = useState<QuestionFormData>(question);
  const [newOption, setNewOption] = useState('');
  const [newTag, setNewTag] = useState('');

  useEffect(() => {
    setFormData(question);
  }, [question]);

  const handleFieldChange = (field: keyof QuestionFormData, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleQuestionTypeChange = (type: string) => {
    const updatedData = {
      ...formData,
      question_type: type,
      options: {},
      correct_answers: [],
    };

    // Set defaults based on question type
    if (type === QuestionType.TRUE_FALSE) {
      updatedData.options = {
        true: 'True',
        false: 'False',
      };
    } else if (type === QuestionType.RATING) {
      updatedData.rating_scale = 5;
    }

    setFormData(updatedData);
  };

  const addOption = () => {
    if (!newOption.trim()) return;

    const optionKey = `option_${Date.now()}`;
    setFormData((prev) => ({
      ...prev,
      options: {
        ...prev.options,
        [optionKey]: newOption.trim(),
      },
    }));
    setNewOption('');
  };

  const removeOption = (optionKey: string) => {
    const { [optionKey]: removed, ...remainingOptions } = formData.options;
    setFormData((prev) => ({
      ...prev,
      options: remainingOptions,
      correct_answers: prev.correct_answers.filter((answer) => answer !== optionKey),
    }));
  };

  const updateOption = (optionKey: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      options: {
        ...prev.options,
        [optionKey]: value,
      },
    }));
  };

  const toggleCorrectAnswer = (optionKey: string) => {
    setFormData((prev) => {
      const isSelected = prev.correct_answers.includes(optionKey);
      let newCorrectAnswers;

      if (
        formData.question_type === QuestionType.SINGLE_CHOICE ||
        formData.question_type === QuestionType.TRUE_FALSE
      ) {
        // Single selection
        newCorrectAnswers = isSelected ? [] : [optionKey];
      } else {
        // Multiple selection
        newCorrectAnswers = isSelected
          ? prev.correct_answers.filter((answer) => answer !== optionKey)
          : [...prev.correct_answers, optionKey];
      }

      return {
        ...prev,
        correct_answers: newCorrectAnswers,
      };
    });
  };

  const addTag = () => {
    if (!newTag.trim() || formData.tags.includes(newTag.trim())) return;

    setFormData((prev) => ({
      ...prev,
      tags: [...prev.tags, newTag.trim()],
    }));
    setNewTag('');
  };

  const removeTag = (tag: string) => {
    setFormData((prev) => ({
      ...prev,
      tags: prev.tags.filter((t) => t !== tag),
    }));
  };

  const handleSave = () => {
    // Validation
    if (!formData.question_text.trim()) {
      alert('Question text is required');
      return;
    }

    if (
      [QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE].includes(
        formData.question_type as any
      )
    ) {
      if (Object.keys(formData.options).length < 2) {
        alert('At least 2 options are required');
        return;
      }
      if (formData.correct_answers.length === 0) {
        alert('At least one correct answer must be selected');
        return;
      }
    }

    onSave(formData);
  };

  const needsOptions = [
    QuestionType.SINGLE_CHOICE,
    QuestionType.MULTIPLE_CHOICE,
    QuestionType.TRUE_FALSE,
  ].includes(formData.question_type as any);
  const needsTextLimits = [QuestionType.TEXT_INPUT, QuestionType.ESSAY].includes(
    formData.question_type as any
  );
  const needsRatingScale = formData.question_type === QuestionType.RATING;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Edit Question</CardTitle>
        <CardDescription>Configure the question details and options</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Basic Information */}
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="question_type">Question Type</Label>
            <Select value={formData.question_type} onValueChange={handleQuestionTypeChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={QuestionType.SINGLE_CHOICE}>Single Choice</SelectItem>
                <SelectItem value={QuestionType.MULTIPLE_CHOICE}>Multiple Choice</SelectItem>
                <SelectItem value={QuestionType.TRUE_FALSE}>True/False</SelectItem>
                <SelectItem value={QuestionType.TEXT_INPUT}>Text Input</SelectItem>
                <SelectItem value={QuestionType.ESSAY}>Essay</SelectItem>
                <SelectItem value={QuestionType.RATING}>Rating Scale</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="points">Points</Label>
              <Input
                id="points"
                type="number"
                value={formData.points}
                onChange={(e) => handleFieldChange('points', parseFloat(e.target.value) || 1)}
                min="0"
                step="0.5"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="time_limit">Time Limit (sec)</Label>
              <Input
                id="time_limit"
                type="number"
                value={formData.time_limit_seconds || ''}
                onChange={(e) =>
                  handleFieldChange(
                    'time_limit_seconds',
                    e.target.value ? parseInt(e.target.value) : null
                  )
                }
                placeholder="No limit"
                min="1"
              />
            </div>
          </div>
        </div>

        {/* Question Text */}
        <div className="space-y-2">
          <Label htmlFor="question_text">Question Text *</Label>
          <Textarea
            id="question_text"
            value={formData.question_text}
            onChange={(e) => handleFieldChange('question_text', e.target.value)}
            placeholder="Enter your question here..."
            rows={3}
          />
        </div>

        {/* Options for Choice Questions */}
        {needsOptions && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>Answer Options</Label>
              <div className="text-sm text-gray-500">
                {formData.question_type === QuestionType.MULTIPLE_CHOICE
                  ? 'Select all correct answers'
                  : 'Select the correct answer'}
              </div>
            </div>

            <div className="space-y-3">
              {Object.entries(formData.options).map(([key, value]) => (
                <div key={key} className="flex items-center gap-3">
                  {formData.question_type === QuestionType.MULTIPLE_CHOICE ? (
                    <Checkbox
                      checked={formData.correct_answers.includes(key)}
                      onCheckedChange={() => toggleCorrectAnswer(key)}
                    />
                  ) : (
                    <RadioGroup
                      value={formData.correct_answers[0] || ''}
                      onValueChange={() => toggleCorrectAnswer(key)}
                    >
                      <RadioGroupItem value={key} />
                    </RadioGroup>
                  )}

                  <Input
                    value={value}
                    onChange={(e) => updateOption(key, e.target.value)}
                    placeholder="Option text"
                    className="flex-1"
                  />

                  {Object.keys(formData.options).length > 2 && (
                    <Button size="sm" variant="outline" onClick={() => removeOption(key)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>

            {formData.question_type !== QuestionType.TRUE_FALSE && (
              <div className="flex gap-2">
                <Input
                  value={newOption}
                  onChange={(e) => setNewOption(e.target.value)}
                  placeholder="Add new option"
                  onKeyPress={(e) => e.key === 'Enter' && addOption()}
                />
                <Button onClick={addOption} size="sm">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Text Limits for Text Questions */}
        {needsTextLimits && (
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="min_length">Minimum Length (characters)</Label>
              <Input
                id="min_length"
                type="number"
                value={formData.min_length || ''}
                onChange={(e) =>
                  handleFieldChange('min_length', e.target.value ? parseInt(e.target.value) : null)
                }
                placeholder="No minimum"
                min="0"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="max_length">Maximum Length (characters)</Label>
              <Input
                id="max_length"
                type="number"
                value={formData.max_length || ''}
                onChange={(e) =>
                  handleFieldChange('max_length', e.target.value ? parseInt(e.target.value) : null)
                }
                placeholder="No maximum"
                min="1"
              />
            </div>
          </div>
        )}

        {/* Rating Scale */}
        {needsRatingScale && (
          <div className="space-y-2">
            <Label htmlFor="rating_scale">Rating Scale (1 to N)</Label>
            <Select
              value={formData.rating_scale?.toString() || '5'}
              onValueChange={(value) => handleFieldChange('rating_scale', parseInt(value))}
            >
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="3">1 to 3</SelectItem>
                <SelectItem value="5">1 to 5</SelectItem>
                <SelectItem value="7">1 to 7</SelectItem>
                <SelectItem value="10">1 to 10</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Explanation */}
        <div className="space-y-2">
          <Label htmlFor="explanation">Explanation (shown to candidates if enabled)</Label>
          <Textarea
            id="explanation"
            value={formData.explanation}
            onChange={(e) => handleFieldChange('explanation', e.target.value)}
            placeholder="Explain the correct answer or provide additional context"
            rows={2}
          />
        </div>

        {/* Tags */}
        <div className="space-y-3">
          <Label>Tags (optional)</Label>
          <div className="flex flex-wrap gap-2 mb-2">
            {formData.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                {tag}
                <button onClick={() => removeTag(tag)} className="ml-1 hover:text-red-600">
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="Add tag"
              onKeyPress={(e) => e.key === 'Enter' && addTag()}
            />
            <Button onClick={addTag} size="sm" variant="outline">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Settings */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center space-x-2">
            <Switch
              id="is_required"
              checked={formData.is_required}
              onCheckedChange={(checked) => handleFieldChange('is_required', checked)}
            />
            <Label htmlFor="is_required">Required Question</Label>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Question
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
