'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  LoadingSpinner,
} from '@/components/ui';
import { Plus, Search, BookOpen, Globe, Building2, Copy } from 'lucide-react';
import { questionBankApi } from '@/api/questionBank';
import type { QuestionBank } from '@/types/questionBank';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';

export default function QuestionBanksPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [banks, setBanks] = useState<QuestionBank[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [examTypeFilter, setExamTypeFilter] = useState('all');
  const [difficultyFilter, setDifficultyFilter] = useState('all');

  const isSystemAdmin = user?.roles?.some(r => r.role.name === 'system_admin');

  useEffect(() => {
    loadQuestionBanks();
  }, [examTypeFilter, difficultyFilter]);

  const loadQuestionBanks = async () => {
    setLoading(true);
    const params: any = {
      include_global: true,
    };

    if (examTypeFilter !== 'all') {
      params.exam_type = examTypeFilter;
    }

    if (difficultyFilter !== 'all') {
      params.difficulty = difficultyFilter;
    }

    const response = await questionBankApi.getQuestionBanks(params);

    if (response.success && response.data) {
      setBanks(response.data.banks);
    } else {
      toast.error(response.message || 'Failed to load question banks');
    }

    setLoading(false);
  };

  const handleCloneBank = async (bankId: number) => {
    const response = await questionBankApi.cloneQuestionBank(bankId);

    if (response.success && response.data) {
      toast.success('Question bank cloned successfully');
      loadQuestionBanks();
    } else {
      toast.error(response.message || 'Failed to clone question bank');
    }
  };

  const filteredBanks = banks.filter(bank =>
    bank.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bank.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container mx-auto py-6 px-4 max-w-7xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Question Banks</h1>
          <p className="text-gray-600">Manage and organize your question collections</p>
        </div>
        <Button asChild>
          <Link href="/admin/question-banks/create">
            <Plus className="h-4 w-4 mr-2" />
            Create Question Bank
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search question banks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            <Select value={examTypeFilter} onValueChange={setExamTypeFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All exam types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Exam Types</SelectItem>
                <SelectItem value="aptitude">Aptitude</SelectItem>
                <SelectItem value="skill">Skill</SelectItem>
                <SelectItem value="knowledge">Knowledge</SelectItem>
                <SelectItem value="personality">Personality</SelectItem>
                <SelectItem value="custom">Custom</SelectItem>
              </SelectContent>
            </Select>

            <Select value={difficultyFilter} onValueChange={setDifficultyFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All difficulties" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Difficulties</SelectItem>
                <SelectItem value="easy">Easy</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="hard">Hard</SelectItem>
                <SelectItem value="mixed">Mixed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Question Banks List */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredBanks.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No question banks found
            </h3>
            <p className="text-gray-600 mb-4">
              {searchTerm
                ? 'Try adjusting your search or filters'
                : 'Create your first question bank to get started'}
            </p>
            <Button asChild>
              <Link href="/admin/question-banks/create">
                <Plus className="h-4 w-4 mr-2" />
                Create Question Bank
              </Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredBanks.map((bank) => (
            <div
              key={bank.id}
              className="cursor-pointer"
              onClick={() => router.push(`/admin/question-banks/${bank.id}`)}
            >
              <Card className="hover:shadow-lg transition-shadow h-full">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg mb-2">{bank.name}</CardTitle>
                    <div className="flex items-center gap-2 mb-2">
                      {bank.company_id === null && (
                        <span className="inline-flex items-center px-2 py-1 rounded-md bg-blue-100 text-blue-700 text-xs">
                          <Globe className="h-3 w-3 mr-1" />
                          Global
                        </span>
                      )}
                      {bank.is_public && (
                        <span className="inline-flex items-center px-2 py-1 rounded-md bg-green-100 text-green-700 text-xs">
                          <Building2 className="h-3 w-3 mr-1" />
                          Public
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <CardDescription className="line-clamp-2">
                  {bank.description || 'No description'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium capitalize">{bank.exam_type}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Questions:</span>
                    <span className="font-medium">{bank.question_count || 0}</span>
                  </div>
                  {bank.difficulty && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Difficulty:</span>
                      <span className="font-medium capitalize">{bank.difficulty}</span>
                    </div>
                  )}
                  {bank.category && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Category:</span>
                      <span className="font-medium">{bank.category}</span>
                    </div>
                  )}
                </div>

                {(bank.is_public || bank.company_id === null) && bank.company_id !== user?.company_id && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full mt-4"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCloneBank(bank.id);
                    }}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Clone to My Company
                  </Button>
                )}
              </CardContent>
            </Card>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
