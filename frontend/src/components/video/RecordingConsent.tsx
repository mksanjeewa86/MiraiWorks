import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { 
  VideoCameraIcon,
  MicrophoneIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';

interface RecordingConsentProps {
  onSubmit: (consented: boolean) => void;
  onClose: () => void;
}

export const RecordingConsent: React.FC<RecordingConsentProps> = ({
  onSubmit,
  onClose,
}) => {
  const [hasRead, setHasRead] = useState(false);

  const handleConsent = (consented: boolean) => {
    onSubmit(consented);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="max-w-md w-full mx-4 p-6">
        <div className="text-center mb-6">
          <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <VideoCameraIcon className="h-8 w-8 text-blue-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            録画と転写の同意
          </h2>
          <p className="text-gray-600">
            この面接の録画と転写について同意をお願いします
          </p>
        </div>

        <div className="space-y-4 mb-6">
          {/* Recording Notice */}
          <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
            <VideoCameraIcon className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-blue-900">ビデオ録画</h4>
              <p className="text-sm text-blue-700">
                この面接セッションは品質向上と記録のために録画されます。
              </p>
            </div>
          </div>

          {/* Audio Recording Notice */}
          <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
            <MicrophoneIcon className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-green-900">音声録音</h4>
              <p className="text-sm text-green-700">
                音声は転写システムによってテキストに変換されます。
              </p>
            </div>
          </div>

          {/* Transcription Notice */}
          <div className="flex items-start space-x-3 p-3 bg-purple-50 rounded-lg">
            <DocumentTextIcon className="h-5 w-5 text-purple-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-purple-900">AI転写</h4>
              <p className="text-sm text-purple-700">
                リアルタイム転写により面接内容がテキスト化されます。
              </p>
            </div>
          </div>
        </div>

        {/* Privacy Notice */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h4 className="font-medium text-gray-900 mb-2">プライバシーについて</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• 録画と転写データは安全に保管されます</li>
            <li>• データは採用プロセスの目的でのみ使用されます</li>
            <li>• 参加者はいつでも録画を停止できます</li>
            <li>• データの削除をリクエストできます</li>
          </ul>
        </div>

        {/* Consent Checkbox */}
        <div className="mb-6">
          <label className="flex items-start space-x-3">
            <input
              type="checkbox"
              checked={hasRead}
              onChange={(e) => setHasRead(e.target.checked)}
              className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">
              上記の内容を読み、理解しました。録画と転写に同意します。
            </span>
          </label>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3">
          <Button
            variant="outline"
            onClick={() => handleConsent(false)}
            className="flex-1"
          >
            同意しない
          </Button>
          <Button
            onClick={() => handleConsent(true)}
            disabled={!hasRead}
            className="flex-1"
          >
            同意する
          </Button>
        </div>

        {/* Skip Option */}
        <div className="text-center mt-4">
          <button
            onClick={onClose}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            後で決定する
          </button>
        </div>
      </Card>
    </div>
  );
};