import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Flag, Send, Loader2 } from 'lucide-react';
import ExamLobby from './ExamLobby';
import ExamResult from './ExamResult';
import QuestionCard from '../../components/exam/QuestionCard';
import QuestionNavigator from '../../components/exam/QuestionNavigator';
import ExamTimer from '../../components/exam/ExamTimer';
import WebcamPreview from '../../components/exam/WebcamPreview';
import ViolationOverlay from '../../components/exam/ViolationOverlay';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import Button from '../../components/ui/Button';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import { examService } from '../../services/examService';
import useExam from '../../hooks/useExam';

export default function TakeExam() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [exam, setExam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isStarting, setIsStarting] = useState(false);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [copyPasteWarned, setCopyPasteWarned] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [isFaceChecking, setIsFaceChecking] = useState(false);

  const violationListenersRef = useRef({});

  const handleViolation = useCallback((type, count, limit) => {
  }, []);

  const handleAutoSubmit = useCallback(() => {
    actions.submitExam('violation');
    showToast('Exam auto-submitted due to too many violations', 'error');
  }, []);

  const { state, actions, derived } = useExam(exam, handleViolation, handleAutoSubmit);

  useEffect(() => {
    loadExam();
  }, [id]);

  const loadExam = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await examService.getExam(id);
      const examData = response.data || response;
      setExam(examData);
    } catch (err) {
      const msg = err?.message || err?.error || 'Failed to load exam';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async (passcode) => {
    setIsStarting(true);
    try {
      await actions.startExam('direct', passcode);
      actions.startAutoSave();
    } catch (err) {
      const msg = err?.message || err?.error || 'Failed to start exam';
      showToast(msg, 'error');
    } finally {
      setIsStarting(false);
    }
  };

  const handleTimeUp = useCallback(() => {
    actions.submitExam('time_up');
    showToast("Time's up! Exam auto-submitted.", 'warning');
  }, [actions]);

  useEffect(() => {
    if (state.phase !== 'in_progress') return;

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        actions.logViolation('tab_switch');
      }
    };

    const handleFullscreenChange = () => {
      if (!document.fullscreenElement && state.phase === 'in_progress') {
        actions.logViolation('fullscreen_exit');
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('fullscreenchange', handleFullscreenChange);

    violationListenersRef.current = {
      handleVisibilityChange,
      handleFullscreenChange,
    };

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, [state.phase, actions]);

  useEffect(() => {
    if (state.phase !== 'in_progress') return;

    const handleKeyDown = (e) => {
      if (state.violationOverlay) {
        e.stopPropagation();
        return;
      }

      const key = e.key.toLowerCase();
      const currentQ = derived.currentQuestion;

      switch (key) {
        case 'arrowright':
        case 'enter':
          e.preventDefault();
          if (!derived.isLastQuestion) {
            actions.goToQuestion(state.currentIndex + 1);
          }
          break;
        case 'arrowleft':
        case 'backspace':
          e.preventDefault();
          if (!derived.isFirstQuestion) {
            actions.goToQuestion(state.currentIndex - 1);
          }
          break;
        case 'f':
          e.preventDefault();
          if (currentQ) {
            actions.toggleFlag(currentQ.id);
          }
          break;
        case '1':
        case 'a':
          e.preventDefault();
          if (currentQ?.options?.[0]) {
            actions.selectOption(currentQ.id, currentQ.options[0].option_id);
          }
          break;
        case '2':
        case 'b':
          e.preventDefault();
          if (currentQ?.options?.[1]) {
            actions.selectOption(currentQ.id, currentQ.options[1].option_id);
          }
          break;
        case '3':
        case 'c':
          e.preventDefault();
          if (currentQ?.options?.[2]) {
            actions.selectOption(currentQ.id, currentQ.options[2].option_id);
          }
          break;
        case '4':
        case 'd':
          e.preventDefault();
          if (currentQ?.options?.[3]) {
            actions.selectOption(currentQ.id, currentQ.options[3].option_id);
          }
          break;
        case 's':
          e.preventDefault();
          if (derived.answeredCount > 0) {
            setShowSubmitDialog(true);
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [state, derived, actions]);

  useEffect(() => {
    if (state.phase !== 'in_progress') return;

    return () => {
      if (state.attemptId && state.phase === 'in_progress') {
        try {
          const backup = JSON.stringify({
            answers: state.answers,
            timestamp: Date.now(),
          });
          localStorage.setItem(`exam_backup_${state.attemptId}`, backup);
        } catch {}
      }
      actions.stopAutoSave();
    };
  }, [state.phase, state.attemptId, state.answers, actions]);

  useEffect(() => {
    if (exam?.security?.camera_required && state.phase === 'in_progress') {
      const initCamera = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ video: true });
          setCameraStream(stream);
        } catch {}
      };
      initCamera();

      return () => {
        if (cameraStream) {
          cameraStream.getTracks().forEach(track => track.stop());
        }
      };
    }
  }, [state.phase, exam?.security?.camera_required]);

  const handleSubmitConfirm = async () => {
    setShowSubmitDialog(false);
    try {
      await actions.submitExam('manual');
    } catch (err) {
      showToast('Submission failed. Please try again.', 'error');
    }
  };

  const handleCopyPaste = (e) => {
    e.preventDefault();
    if (!copyPasteWarned) {
      actions.logViolation('copy_paste');
      setCopyPasteWarned(true);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading exam...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Unable to Load Exam</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Button onClick={() => navigate('/dashboard/student')}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  if (state.phase === 'lobby' || state.phase === 'starting') {
    return (
      <ExamLobby
        exam={exam}
        onStart={handleStart}
        isStarting={isStarting || state.phase === 'starting'}
      />
    );
  }

  if (state.phase === 'submitting') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Submitting Exam...</h2>
          <p className="text-gray-600">Please wait while we save your answers.</p>
        </div>
      </div>
    );
  }

  if (state.phase === 'submitted' && state.result) {
    return (
      <ExamResult
        result={state.result}
        exam={exam}
        isAutoSubmitted={false}
        submissionReason={null}
      />
    );
  }

  const currentQ = derived.currentQuestion;
  const currentAnswer = derived.currentAnswer;

  const hasViolationOnQuestion = state.violations.some(
    v => v.questionId === currentQ?.question_id
  );

  return (
    <div
      className="min-h-screen bg-gray-100"
      onCopy={handleCopyPaste}
      onPaste={handleCopyPaste}
      onCut={handleCopyPaste}
      onContextMenu={handleCopyPaste}
    >
      {state.violationOverlay && (
        <ViolationOverlay
          type={state.violationOverlay.type}
          count={state.violationOverlay.count}
          limit={state.violationOverlay.limit}
          onDismiss={actions.dismissViolationOverlay}
          onFullscreenReturn={actions.returnToFullscreen}
        />
      )}

      <ConfirmDialog
        isOpen={showSubmitDialog}
        onConfirm={handleSubmitConfirm}
        onCancel={() => setShowSubmitDialog(false)}
        title="Submit Exam?"
        message={`You have answered ${derived.answeredCount} of ${derived.totalQuestions} questions.${
          derived.totalQuestions - derived.answeredCount > 0
            ? ` ${derived.totalQuestions - derived.answeredCount} questions are still unanswered.`
            : ''
        } Are you sure you want to submit?`}
        confirmLabel="Submit Exam"
        confirmVariant="success"
      />

      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <h1 className="text-lg font-bold text-gray-900 truncate max-w-md">
                {exam?.title}
              </h1>
              {state.saveStatus === 'saving' && (
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Saving...
                </span>
              )}
              {state.saveStatus === 'saved' && (
                <span className="text-xs text-green-600">Saved</span>
              )}
              {state.saveStatus === 'error' && (
                <span className="text-xs text-red-600">Save failed</span>
              )}
            </div>

            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-500">
                <span className="font-medium text-gray-900">{derived.answeredCount}</span>
                <span className="mx-1">/</span>
                <span>{derived.totalQuestions}</span>
                <span className="ml-1">answered</span>
              </div>

              <ExamTimer
                durationMinutes={state.examConfig?.duration_minutes || exam?.duration_minutes || 60}
                serverStartTime={state.serverStartTime}
                onTimeUp={handleTimeUp}
              />

              <Button
                onClick={() => setShowSubmitDialog(true)}
                variant="success"
                size="sm"
                leftIcon={<Send className="w-4 h-4" />}
              >
                Submit
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          <div className="flex-1 min-w-0">
            {currentQ && (
              <QuestionCard
                question={currentQ}
                questionNumber={state.currentIndex + 1}
                totalQuestions={derived.totalQuestions}
                selectedOptionId={currentAnswer?.selectedOptionId || null}
                flagged={currentAnswer?.flagged || false}
                onSelect={(optionId) => actions.selectOption(currentQ.id, optionId)}
                onFlag={() => actions.toggleFlag(currentQ.id)}
                showViolation={hasViolationOnQuestion}
              />
            )}

            <div className="mt-6 flex items-center justify-between">
              <Button
                variant="secondary"
                onClick={() => actions.goToQuestion(state.currentIndex - 1)}
                disabled={derived.isFirstQuestion}
                leftIcon={<ArrowLeft className="w-4 h-4" />}
              >
                Previous
              </Button>

              <div className="flex items-center gap-2">
                <Button
                  variant={currentAnswer?.flagged ? 'warning' : 'ghost'}
                  onClick={() => currentQ && actions.toggleFlag(currentQ.id)}
                  leftIcon={<Flag className={`w-4 h-4 ${currentAnswer?.flagged ? 'fill-current' : ''}`} />}
                  disabled={!currentQ}
                >
                  {currentAnswer?.flagged ? 'Unflag' : 'Flag'}
                </Button>
              </div>

              <Button
                variant="primary"
                onClick={() => actions.goToQuestion(state.currentIndex + 1)}
                disabled={derived.isLastQuestion}
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Next
              </Button>
            </div>
          </div>

          <div className="w-80 flex-shrink-0 space-y-4">
            <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Time Remaining</h3>
              <div className="flex justify-center">
                <ExamTimer
                  durationMinutes={state.examConfig?.duration_minutes || exam?.duration_minutes || 60}
                  serverStartTime={state.serverStartTime}
                  onTimeUp={handleTimeUp}
                />
              </div>
            </div>

            <QuestionNavigator
              questions={state.questions}
              answers={state.answers}
              violations={state.violations}
              currentIndex={state.currentIndex}
              onNavigate={actions.goToQuestion}
            />

            <Button
              onClick={() => setShowSubmitDialog(true)}
              variant="success"
              className="w-full"
              leftIcon={<Send className="w-4 h-4" />}
            >
              Submit Exam ({derived.answeredCount}/{derived.totalQuestions})
            </Button>
          </div>
        </div>
      </div>

      {exam?.security?.camera_required && cameraStream && (
        <WebcamPreview
          stream={cameraStream}
          isChecking={isFaceChecking}
          violations={state.violations.filter(v => v.type === 'face_mismatch').length}
        />
      )}
    </div>
  );
}
