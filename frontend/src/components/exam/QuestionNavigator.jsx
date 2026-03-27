import React from 'react';
import { Bookmark } from 'lucide-react';

const QuestionNavigator = ({
  questions,
  answers,
  violations,
  currentIndex,
  onNavigate,
}) => {
  const hasViolation = (questionId) => {
    return violations.some(v => v.questionId === questionId);
  };

  const getButtonColor = (questionId, index) => {
    const answer = answers[questionId];
    const isFlagged = answer?.flagged || false;
    const hasViolationOnQuestion = hasViolation(questionId);

    if (hasViolationOnQuestion) {
      return 'bg-red-600 text-white hover:bg-red-700';
    }
    if (isFlagged) {
      return 'bg-amber-600 text-white hover:bg-amber-700';
    }
    if (answer?.selectedOptionId) {
      return 'bg-green-600 text-white hover:bg-green-700';
    }
    return 'bg-gray-300 text-gray-700 hover:bg-gray-400';
  };

  const getCurrentIndexValue = () => {
    return currentIndex;
  };

  const gridCols = questions.length <= 10 ? 'grid-cols-5' : 'grid-cols-6';

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">
        Question Navigator
      </h3>
      
      <div className={`grid ${gridCols} gap-2`}>
        {questions.map((question, index) => {
          const questionId = question.id;
          const answer = answers[questionId];
          const isFlagged = answer?.flagged || false;
          const isCurrent = index === currentIndex;
          const isViolated = hasViolation(questionId);

          return (
            <button
              key={questionId}
              onClick={() => onNavigate(index)}
              className={`
                relative flex items-center justify-center h-10 rounded-lg text-sm font-medium
                transition-all duration-150
                ${getButtonColor(questionId, index)}
                ${isCurrent ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
              `}
            >
              <span>{index + 1}</span>
              {isFlagged && (
                <Bookmark className="absolute -top-1 -right-1 w-3 h-3 text-amber-600 fill-current" />
              )}
              {isViolated && !isFlagged && (
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full" />
              )}
            </button>
          );
        })}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex flex-wrap gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-gray-300" />
            <span className="text-gray-600">Unanswered</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-green-600" />
            <span className="text-gray-600">Answered</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-amber-600" />
            <span className="text-gray-600">Flagged</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-red-600" />
            <span className="text-gray-600">Violation</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionNavigator;