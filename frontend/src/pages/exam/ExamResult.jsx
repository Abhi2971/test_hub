import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, XCircle, Award, TrendingUp, Clock, AlertTriangle, Download, RefreshCw, Loader2 } from 'lucide-react';
import Button from '../../components/ui/Button';
import TopicBarChart from '../../components/charts/TopicBarChart';
import { resultService } from '../../services/resultService';

export default function ExamResult({ result, exam, isAutoSubmitted, submissionReason }) {
  const navigate = useNavigate();
  const [aiRecommendation, setAiRecommendation] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [downloadingCert, setDownloadingCert] = useState(false);

  const isDelayed = exam?.result_mode === 'delayed' || result?.status === 'pending';

  useEffect(() => {
    if (!isDelayed && result?.result_id) {
      pollAIRecommendations();
    }
  }, [isDelayed, result?.result_id]);

  const pollAIRecommendations = async () => {
    if (!result?.result_id) return;

    setAiLoading(true);
    let attempts = 0;
    const maxAttempts = 12;

    const poll = async () => {
      if (attempts >= maxAttempts) {
        setAiLoading(false);
        return;
      }

      try {
        const response = await resultService.getAIRecommendation(result.result_id);
        const data = response.data || response;

        if (data.status === 'completed' && data.recommendations) {
          setAiRecommendation(data.recommendations);
          setAiLoading(false);
        } else if (data.status === 'failed') {
          setAiRecommendation({ error: 'AI analysis failed. Please try again later.' });
          setAiLoading(false);
        } else {
          attempts++;
          setTimeout(poll, 5000);
        }
      } catch {
        attempts++;
        setTimeout(poll, 5000);
      }
    };

    poll();
  };

  const handleDownloadCertificate = async () => {
    if (!result?.result_id) return;

    setDownloadingCert(true);
    try {
      const response = await resultService.downloadCertificate(result.result_id);
      const data = response.data || response;

      if (data.certificate_url) {
        window.open(data.certificate_url, '_blank');
      } else if (data.url) {
        window.open(data.url, '_blank');
      } else if (data.download_url) {
        window.open(data.download_url, '_blank');
      } else {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `certificate-${result.result_id}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('Certificate download failed:', err);
    } finally {
      setDownloadingCert(false);
    }
  };

  const getGrade = (percentage) => {
    if (percentage >= 90) return { letter: 'A+', color: 'bg-green-500' };
    if (percentage >= 80) return { letter: 'A', color: 'bg-green-400' };
    if (percentage >= 70) return { letter: 'B+', color: 'bg-blue-500' };
    if (percentage >= 60) return { letter: 'B', color: 'bg-blue-400' };
    if (percentage >= 50) return { letter: 'C', color: 'bg-yellow-500' };
    if (percentage >= 40) return { letter: 'D', color: 'bg-orange-500' };
    return { letter: 'F', color: 'bg-red-500' };
  };

  const answeredCount = result?.answered_count || result?.stats?.answered || 0;
  const totalQuestions = result?.total_questions || exam?.questions?.length || 0;
  const unansweredCount = totalQuestions - answeredCount;
  const score = result?.score ?? result?.obtained_marks ?? 0;
  const totalMarks = result?.total_marks || exam?.total_marks || totalQuestions;
  const percentage = totalMarks > 0 ? Math.round((score / totalMarks) * 100) : 0;
  const passed = result?.passed ?? (percentage >= (exam?.passing_score || 50));
  const grade = getGrade(percentage);

  const topicData = result?.topic_breakdown || result?.topic_performance || [];
  const formattedTopicData = topicData.length > 0
    ? topicData.map(t => ({ topic: t.topic || 'General', correct: t.correct || 0, wrong: t.wrong || 0 }))
    : [];

  const handleBackToDashboard = () => {
    navigate('/dashboard/student');
  };

  if (isDelayed) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-6">
        <div className="max-w-lg w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Clock className="w-10 h-10 text-blue-600" />
          </div>

          <h1 className="text-2xl font-bold text-gray-900 mb-2">Exam Submitted</h1>
          <p className="text-gray-600 mb-6">
            Your exam has been submitted successfully. Your teacher will publish results soon.
          </p>

          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Answered</p>
                <p className="font-semibold text-gray-900">{answeredCount}</p>
              </div>
              <div>
                <p className="text-gray-500">Unanswered</p>
                <p className="font-semibold text-gray-900">{unansweredCount}</p>
              </div>
              <div>
                <p className="text-gray-500">Violations</p>
                <p className="font-semibold text-gray-900">{result?.violations_count || 0}</p>
              </div>
            </div>
          </div>

          <Button onClick={handleBackToDashboard} className="w-full">
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className={`px-8 py-6 ${passed ? 'bg-gradient-to-r from-green-500 to-emerald-600' : 'bg-gradient-to-r from-red-500 to-rose-600'}`}>
            <div className="flex items-center justify-between">
              <div className="text-white">
                <h1 className="text-2xl font-bold">{exam?.title || 'Exam'} — Results</h1>
                <p className="text-sm text-white/80 mt-1">
                  {isAutoSubmitted
                    ? `Auto-submitted: ${submissionReason === 'time_up' ? "Time's up" : 'Too many violations'}`
                    : 'Exam completed successfully'}
                </p>
              </div>
              <div className={`px-6 py-3 rounded-xl ${passed ? 'bg-white/20' : 'bg-white/20'}`}>
                <p className="text-white/80 text-sm">Your Score</p>
                <p className="text-3xl font-bold text-white">{score} / {totalMarks}</p>
              </div>
            </div>
          </div>

          <div className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-blue-50 rounded-xl p-4 text-center">
                <p className="text-sm text-blue-600 font-medium">Percentage</p>
                <p className="text-2xl font-bold text-blue-900 mt-1">{percentage}%</p>
              </div>

              <div className="bg-purple-50 rounded-xl p-4 text-center">
                <p className="text-sm text-purple-600 font-medium">Grade</p>
                <div className="flex items-center justify-center gap-2 mt-1">
                  <span className={`w-10 h-10 rounded-full ${grade.color} text-white text-lg font-bold flex items-center justify-center`}>
                    {grade.letter}
                  </span>
                </div>
              </div>

              <div className="bg-green-50 rounded-xl p-4 text-center">
                <p className="text-sm text-green-600 font-medium">Status</p>
                <div className="flex items-center justify-center gap-2 mt-2">
                  {passed ? (
                    <>
                      <CheckCircle2 className="w-5 h-5 text-green-600" />
                      <span className="text-lg font-bold text-green-700">Passed</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-5 h-5 text-red-600" />
                      <span className="text-lg font-bold text-red-700">Failed</span>
                    </>
                  )}
                </div>
              </div>

              <div className="bg-amber-50 rounded-xl p-4 text-center">
                <p className="text-sm text-amber-600 font-medium">Time Taken</p>
                <p className="text-2xl font-bold text-amber-900 mt-1">
                  {result?.time_taken_minutes || result?.time_spent || '?'}m
                </p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-500">Correct</p>
                <p className="text-xl font-bold text-green-600">{result?.correct_count || 0}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-500">Wrong</p>
                <p className="text-xl font-bold text-red-600">{result?.wrong_count || 0}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-500">Unanswered</p>
                <p className="text-xl font-bold text-gray-600">{unansweredCount}</p>
              </div>
            </div>

            {(result?.violations_count > 0 || result?.violations?.length > 0) && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex items-center gap-2 text-red-800">
                  <AlertTriangle className="w-5 h-5" />
                  <span className="font-semibold">
                    {result?.violations_count || result?.violations?.length || 0} violation(s) recorded
                  </span>
                </div>
              </div>
            )}

            {formattedTopicData.length > 0 && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Topic-wise Performance
                </h3>
                <TopicBarChart data={formattedTopicData} title="" />
              </div>
            )}

            {aiLoading && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6 flex items-center gap-4">
                <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
                <div>
                  <p className="font-semibold text-blue-900">AI Analysis in Progress</p>
                  <p className="text-sm text-blue-700">Generating personalized recommendations...</p>
                </div>
              </div>
            )}

            {aiRecommendation && !aiRecommendation.error && (
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-semibold text-indigo-900 mb-4 flex items-center gap-2">
                  <Award className="w-5 h-5" />
                  AI Recommendations
                </h3>
                <div className="space-y-3">
                  {aiRecommendation.topics_to_improve?.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-indigo-800">Topics to Improve:</p>
                      <ul className="mt-1 space-y-1">
                        {aiRecommendation.topics_to_improve.map((topic, i) => (
                          <li key={i} className="text-sm text-indigo-700 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                            {topic}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {aiRecommendation.study_tips?.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-indigo-800 mt-3">Study Tips:</p>
                      <ul className="mt-1 space-y-1">
                        {aiRecommendation.study_tips.map((tip, i) => (
                          <li key={i} className="text-sm text-indigo-700 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                            {tip}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {aiRecommendation.strengths?.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-indigo-800 mt-3">Your Strengths:</p>
                      <ul className="mt-1 space-y-1">
                        {aiRecommendation.strengths.map((s, i) => (
                          <li key={i} className="text-sm text-indigo-700 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {aiRecommendation?.error && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6 text-center">
                <p className="text-gray-600 text-sm">{aiRecommendation.error}</p>
                <button
                  onClick={pollAIRecommendations}
                  className="mt-2 text-blue-600 text-sm hover:underline flex items-center gap-1 mx-auto"
                >
                  <RefreshCw className="w-4 h-4" />
                  Try Again
                </button>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3">
              {passed && exam?.certificate_enabled && (
                <Button
                  onClick={handleDownloadCertificate}
                  loading={downloadingCert}
                  leftIcon={<Download className="w-4 h-4" />}
                  className="flex-1"
                >
                  Download Certificate
                </Button>
              )}
              <Button onClick={handleBackToDashboard} variant="secondary" className="flex-1">
                Back to Dashboard
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
