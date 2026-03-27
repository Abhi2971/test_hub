import { useState, useEffect } from 'react';
import { CheckCircle2, XCircle, Loader2, AlertCircle, Camera, Maximize2, Wifi, Shield } from 'lucide-react';
import Button from '../../components/ui/Button';

export default function ExamLobby({ exam, onStart, isStarting }) {
  const [checks, setChecks] = useState({
    fullscreen: { status: 'pending', message: 'Checking fullscreen support...' },
    internet: { status: 'pending', message: 'Checking internet connection...' },
    camera: { status: 'pending', message: 'Requesting camera access...' },
    passcode: { status: exam?.security?.passcode ? 'pending' : 'skipped', message: exam?.security?.passcode ? 'Passcode required' : 'No passcode required' },
  });

  const [cameraStream, setCameraStream] = useState(null);
  const [passcode, setPasscode] = useState('');
  const [passcodeError, setPasscodeError] = useState('');
  const [cameraError, setCameraError] = useState(null);

  useEffect(() => {
    runChecks();
    return () => {
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const runChecks = async () => {
    if (document.fullscreenEnabled) {
      setChecks(prev => ({ ...prev, fullscreen: { status: 'success', message: 'Fullscreen supported' } }));
    } else {
      setChecks(prev => ({ ...prev, fullscreen: { status: 'warning', message: 'Fullscreen may not work in this browser' } }));
    }

    if (navigator.onLine) {
      setChecks(prev => ({ ...prev, internet: { status: 'success', message: 'Internet connection active' } }));
    } else {
      setChecks(prev => ({ ...prev, internet: { status: 'error', message: 'No internet connection' } }));
    }

    if (exam?.security?.camera_required) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        setCameraStream(stream);
        setChecks(prev => ({ ...prev, camera: { status: 'success', message: 'Camera access granted' } }));
      } catch (err) {
        setCameraError(err.message || 'Camera access denied');
        setChecks(prev => ({ ...prev, camera: { status: 'error', message: 'Camera access denied' } }));
      }
    } else {
      setChecks(prev => ({ ...prev, camera: { status: 'skipped', message: 'Camera not required' } }));
    }
  };

  const handleStart = () => {
    if (exam?.security?.passcode) {
      if (!passcode.trim()) {
        setPasscodeError('Passcode is required');
        return;
      }
      setPasscodeError('');
    }
    onStart(passcode.trim());
  };

  const allChecksPass = Object.values(checks).every(
    c => c.status === 'success' || c.status === 'skipped' || c.status === 'warning'
  );

  const canStart = allChecksPass && (!exam?.security?.passcode || passcode.trim());

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-amber-500" />;
      case 'skipped':
        return <CheckCircle2 className="w-5 h-5 text-gray-400" />;
      default:
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'border-green-200 bg-green-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      case 'warning':
        return 'border-amber-200 bg-amber-50';
      case 'skipped':
        return 'border-gray-200 bg-gray-50';
      default:
        return 'border-blue-200 bg-blue-50';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full space-y-6">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6">
            <h1 className="text-2xl font-bold text-white">{exam?.title || 'Exam'}</h1>
            <p className="text-blue-100 mt-1">{exam?.subject || exam?.description || 'Take your exam'}</p>
          </div>

          <div className="p-8 space-y-6">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-500 text-xs uppercase tracking-wide">Duration</p>
                <p className="font-semibold text-gray-900 mt-1">{exam?.duration_minutes || exam?.duration || '?'} minutes</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-500 text-xs uppercase tracking-wide">Questions</p>
                <p className="font-semibold text-gray-900 mt-1">{exam?.questions?.length || exam?.total_questions || '?'}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-500 text-xs uppercase tracking-wide">Total Marks</p>
                <p className="font-semibold text-gray-900 mt-1">{exam?.total_marks || '?'}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-500 text-xs uppercase tracking-wide">Passing Score</p>
                <p className="font-semibold text-gray-900 mt-1">{exam?.passing_score || '?'}%</p>
              </div>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-amber-800">
                <p className="font-semibold">Important Instructions</p>
                <ul className="mt-2 space-y-1 text-amber-700">
                  <li>Do not switch tabs or leave the exam window</li>
                  <li>Stay in fullscreen mode throughout the exam</li>
                  <li>Tab switching limit: {exam?.security?.tab_switch_limit || 'unlimited'} warnings</li>
                  {exam?.security?.camera_required && (
                    <li>Camera must remain on during the exam</li>
                  )}
                </ul>
              </div>
            </div>

            <div className="border rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-3 border-b">
                <h3 className="font-semibold text-gray-900">Pre-Exam Checklist</h3>
              </div>
              <div className="divide-y">
                <div className={`p-4 flex items-center gap-4 transition-colors ${getStatusColor(checks.fullscreen.status)}`}>
                  {getStatusIcon(checks.fullscreen.status)}
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 flex items-center gap-2">
                      <Maximize2 className="w-4 h-4" />
                      Fullscreen Mode
                    </p>
                    <p className="text-sm text-gray-600">{checks.fullscreen.message}</p>
                  </div>
                </div>

                <div className={`p-4 flex items-center gap-4 transition-colors ${getStatusColor(checks.internet.status)}`}>
                  {getStatusIcon(checks.internet.status)}
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 flex items-center gap-2">
                      <Wifi className="w-4 h-4" />
                      Internet Connection
                    </p>
                    <p className="text-sm text-gray-600">{checks.internet.message}</p>
                  </div>
                </div>

                <div className={`p-4 flex items-center gap-4 transition-colors ${getStatusColor(checks.camera.status)}`}>
                  {getStatusIcon(checks.camera.status)}
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 flex items-center gap-2">
                      <Camera className="w-4 h-4" />
                      Camera Access
                    </p>
                    <p className="text-sm text-gray-600">{checks.camera.message}</p>
                    {cameraError && (
                      <p className="text-sm text-red-600 mt-1">{cameraError}</p>
                    )}
                  </div>
                  {cameraStream && (
                    <video
                      autoPlay
                      muted
                      playsInline
                      className="w-20 h-15 rounded-lg object-cover border"
                      ref={(el) => {
                        if (el && cameraStream) el.srcObject = cameraStream;
                      }}
                    />
                  )}
                </div>

                {exam?.security?.passcode ? (
                  <div className={`p-4 transition-colors ${passcodeError ? 'bg-red-50 border-l-4 border-red-500' : 'bg-gray-50'}`}>
                    <div className="flex items-center gap-4">
                      <Shield className="w-5 h-5 text-gray-600" />
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">Exam Passcode</p>
                        <input
                          type="password"
                          value={passcode}
                          onChange={(e) => {
                            setPasscode(e.target.value);
                            setPasscodeError('');
                          }}
                          placeholder="Enter passcode"
                          className="mt-2 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                          disabled={isStarting}
                        />
                        {passcodeError && (
                          <p className="text-sm text-red-600 mt-1">{passcodeError}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 flex items-center gap-4 bg-gray-50">
                    {getStatusIcon('skipped')}
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        Exam Passcode
                      </p>
                      <p className="text-sm text-gray-500">No passcode required</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <Button
              onClick={handleStart}
              disabled={!canStart || isStarting}
              loading={isStarting}
              className="w-full py-4 text-lg font-semibold"
              size="lg"
            >
              {isStarting ? 'Starting Exam...' : 'Start Exam'}
            </Button>

            <p className="text-center text-xs text-gray-500">
              By clicking "Start Exam", you agree to the exam rules and acknowledge that your activity may be monitored.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
