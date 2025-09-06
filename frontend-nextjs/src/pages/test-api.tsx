import { NextPage } from 'next';
import Head from 'next/head';
import ApiTestRunner from '@/components/ApiTestRunner';

const TestApiPage: NextPage = () => {
  return (
    <>
      <Head>
        <title>API Test Runner - MiraiWorks</title>
        <meta name="description" content="Test all API endpoints" />
      </Head>
      
      <div className="min-h-screen bg-gray-100">
        <ApiTestRunner />
      </div>
    </>
  );
};

export default TestApiPage;