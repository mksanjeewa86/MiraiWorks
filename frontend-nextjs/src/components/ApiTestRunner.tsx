import React, { useState } from 'react';
import { authApi } from '@/services/authApi';
import { dashboardApi } from '@/services/dashboardApi';
import { messagesApi } from '@/services/messagesApi';
import { resumesApi } from '@/services/resumesApi';

interface TestResult {
  name: string;
  status: 'pass' | 'fail' | 'pending';
  details: string;
  duration?: number;
}

interface TestSuite {
  name: string;
  tests: TestResult[];
  completed: boolean;
}

const ApiTestRunner: React.FC = () => {
  const [testSuites, setTestSuites] = useState<TestSuite[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [accessToken, setAccessToken] = useState<string>('');

  const updateTestResult = (suiteName: string, testName: string, result: Partial<TestResult>) => {
    setTestSuites(prev => 
      prev.map(suite => 
        suite.name === suiteName 
          ? {
              ...suite,
              tests: suite.tests.map(test => 
                test.name === testName 
                  ? { ...test, ...result }
                  : test
              )
            }
          : suite
      )
    );
  };

  const addTestSuite = (name: string, testNames: string[]) => {
    const tests = testNames.map(name => ({
      name,
      status: 'pending' as const,
      details: ''
    }));
    
    setTestSuites(prev => [...prev, { name, tests, completed: false }]);
  };

  const markSuiteCompleted = (suiteName: string) => {
    setTestSuites(prev =>
      prev.map(suite =>
        suite.name === suiteName
          ? { ...suite, completed: true }
          : suite
      )
    );
  };

  const runTest = async (testName: string, testFn: () => Promise<unknown>): Promise<TestResult> => {
    const start = Date.now();
    try {
      await testFn();
      const duration = Date.now() - start;
      return {
        name: testName,
        status: 'pass',
        details: 'Success',
        duration
      };
    } catch (error) {
      const duration = Date.now() - start;
      return {
        name: testName,
        status: 'fail',
        details: error instanceof Error ? error.message : 'Unknown error',
        duration
      };
    }
  };

  const runAuthTests = async () => {
    const suiteName = 'Authentication API';
    const testNames = [
      'Login with valid credentials',
      'Get current user profile',
      'Refresh token'
    ];
    
    addTestSuite(suiteName, testNames);

    // Test login
    const loginResult = await runTest(
      'Login with valid credentials',
      async () => {
        const response = await authApi.login({
          email: 'admin@miraiworks.com',
          password: 'admin123'
        });
        if (response.data && response.data.access_token) {
          setAccessToken(response.data.access_token);
          return response;
        }
        throw new Error('No access token received');
      }
    );
    updateTestResult(suiteName, 'Login with valid credentials', loginResult);

    // Test get current user (requires token)
    if (accessToken || loginResult.status === 'pass') {
      const token = accessToken || 'test-token';
      const meResult = await runTest(
        'Get current user profile',
        () => authApi.me(token)
      );
      updateTestResult(suiteName, 'Get current user profile', meResult);
    }

    // Test refresh token (will likely fail without proper refresh token)
    const refreshResult = await runTest(
      'Refresh token',
      () => authApi.refreshToken('invalid-token')
    );
    updateTestResult(suiteName, 'Refresh token', refreshResult);

    markSuiteCompleted(suiteName);
  };

  const runDashboardTests = async () => {
    const suiteName = 'Dashboard API';
    const testNames = [
      'Get dashboard statistics',
      'Get activity feed'
    ];
    
    addTestSuite(suiteName, testNames);

    if (!accessToken) {
      testNames.forEach(testName => {
        updateTestResult(suiteName, testName, {
          status: 'fail',
          details: 'No access token available'
        });
      });
      markSuiteCompleted(suiteName);
      return;
    }

    // Test dashboard stats
    const statsResult = await runTest(
      'Get dashboard statistics',
      () => dashboardApi.getStats(accessToken)
    );
    updateTestResult(suiteName, 'Get dashboard statistics', statsResult);

    // Test activity feed
    const activityResult = await runTest(
      'Get activity feed',
      () => dashboardApi.getRecentActivity(10, accessToken)
    );
    updateTestResult(suiteName, 'Get activity feed', activityResult);

    markSuiteCompleted(suiteName);
  };

  const runMessagingTests = async () => {
    const suiteName = 'Messaging API';
    const testNames = [
      'Get conversations',
      'Mark conversation as read'
    ];
    
    addTestSuite(suiteName, testNames);

    if (!accessToken) {
      testNames.forEach(testName => {
        updateTestResult(suiteName, testName, {
          status: 'fail',
          details: 'No access token available'
        });
      });
      markSuiteCompleted(suiteName);
      return;
    }

    // Test get conversations
    const conversationsResult = await runTest(
      'Get conversations',
      () => messagesApi.getConversations(accessToken)
    );
    updateTestResult(suiteName, 'Get conversations', conversationsResult);

    // Test mark as read
    const markReadResult = await runTest(
      'Mark conversation as read',
      () => messagesApi.markConversationAsRead(1, accessToken)
    );
    updateTestResult(suiteName, 'Mark conversation as read', markReadResult);

    markSuiteCompleted(suiteName);
  };

  const runResumeTests = async () => {
    const suiteName = 'Resume API';
    const testNames = [
      'Get resumes list',
      'Get resume statistics'
    ];
    
    addTestSuite(suiteName, testNames);

    if (!accessToken) {
      testNames.forEach(testName => {
        updateTestResult(suiteName, testName, {
          status: 'fail',
          details: 'No access token available'
        });
      });
      markSuiteCompleted(suiteName);
      return;
    }

    // Test get resumes
    const resumesResult = await runTest(
      'Get resumes list',
      async () => {
        // Temporarily store token in localStorage for API call
        const oldToken = localStorage.getItem('accessToken');
        localStorage.setItem('accessToken', accessToken);
        try {
          return await resumesApi.getAll();
        } finally {
          if (oldToken) {
            localStorage.setItem('accessToken', oldToken);
          } else {
            localStorage.removeItem('accessToken');
          }
        }
      }
    );
    updateTestResult(suiteName, 'Get resumes list', resumesResult);

    // Test resume stats (API endpoint might not exist yet)
    const statsResult = await runTest(
      'Get resume statistics',
      async () => {
        const response = await fetch(`http://localhost:8000/api/resumes/stats`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      }
    );
    updateTestResult(suiteName, 'Get resume statistics', statsResult);

    markSuiteCompleted(suiteName);
  };

  const runAllTests = async () => {
    setIsRunning(true);
    setTestSuites([]);
    setAccessToken('');

    try {
      await runAuthTests();
      await runDashboardTests();
      await runMessagingTests();
      await runResumeTests();
    } finally {
      setIsRunning(false);
    }
  };

  const getTotalStats = () => {
    const allTests = testSuites.flatMap(suite => suite.tests);
    const passed = allTests.filter(test => test.status === 'pass').length;
    const failed = allTests.filter(test => test.status === 'fail').length;
    const total = allTests.length;
    
    return { passed, failed, total };
  };

  const stats = getTotalStats();

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Frontend API Test Runner</h1>
        <p className="text-gray-600">
          Test all frontend API service calls to ensure they work correctly.
        </p>
      </div>

      <div className="mb-6 flex items-center gap-4">
        <button
          onClick={runAllTests}
          disabled={isRunning}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {isRunning ? 'Running Tests...' : 'Run All Tests'}
        </button>

        {stats.total > 0 && (
          <div className="text-sm text-gray-600">
            Total: {stats.total} | Passed: {stats.passed} | Failed: {stats.failed} | 
            Success Rate: {((stats.passed / stats.total) * 100).toFixed(1)}%
          </div>
        )}
      </div>

      {testSuites.map((suite) => (
        <div key={suite.name} className="mb-6 border rounded-lg">
          <div className="bg-gray-50 px-4 py-2 border-b">
            <h2 className="font-semibold">{suite.name}</h2>
          </div>
          <div className="p-4">
            {suite.tests.map((test) => (
              <div
                key={test.name}
                className={`flex items-center justify-between py-2 px-3 rounded mb-2 ${{
                  pass: 'bg-green-50 border-green-200',
                  fail: 'bg-red-50 border-red-200',
                  pending: 'bg-gray-50 border-gray-200'
                }[test.status]} border`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${{
                    pass: 'bg-green-500',
                    fail: 'bg-red-500',
                    pending: 'bg-gray-400'
                  }[test.status]}`} />
                  <span className="font-medium">{test.name}</span>
                </div>
                <div className="text-sm text-gray-600 flex items-center gap-2">
                  {test.duration && <span>{test.duration}ms</span>}
                  <span className={`font-medium ${{
                    pass: 'text-green-700',
                    fail: 'text-red-700',
                    pending: 'text-gray-500'
                  }[test.status]}`}>
                    {{
                      pass: 'PASS',
                      fail: 'FAIL',
                      pending: 'PENDING'
                    }[test.status]}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {testSuites.length === 0 && !isRunning && (
        <div className="text-center text-gray-500 py-8">
          Click &quot;Run All Tests&quot; to start testing the API endpoints.
        </div>
      )}
    </div>
  );
};

export default ApiTestRunner;