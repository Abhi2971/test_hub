import React, { useEffect } from 'react';
import { Bookmark, BookmarkCheck, AlertCircle } from 'lucide-react';

const QuestionCard = ({
  question,
  questionNumber,
  totalQuestions,
  selectedOptionId,
  flagged,
  onSelect,
  onFlag,
  showViolation = false,
}) => {
  const optionLetters = ['A', 'B', 'C', 'D'];

  useEffect(() => {
    const handleKeyDown = (e) => {
      const key = e.key.toLowerCase();
      const optionIndex = ['1', 'a', '2', 'b', '3', 'c', '4', 'd'].indexOf(key);
      
      if (optionIndex !== -1 && question.options[optionIndex]) {
        onSelect(question.options[optionIndex].option_id);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [question.options, onSelect]);

  const handleCopy = (e) => {
    e.preventDefault();
  };

  const difficultyColors = {
    easy: 'bg-green-100 text-green-700',
    medium: 'bg-yellow-100 text-yellow-700',
    hard: 'bg-red-100 text-red-700',
  };

  const getDifficultyBadge = () => {
    const diff = question.difficulty?.toLowerCase() || 'medium';
    return difficultyColors[diff] || difficultyColors.medium;
  };

  return (
    <div
      className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm"
      onCopy={handleCopy}
      onPaste={handleCopy}
      onCut={handleCopy}
      onContextMenu={handleCopy}
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-gray-600">
          Question {questionNumber} of {totalQuestions}
        </span>
        
        {showViolation && (
          <div className="flex items-center gap-1.5 bg-red-50 text-red-600 px-2.5 py-1 rounded-full text-xs font-medium">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Violation</span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-2 mb-4">
        <span className="bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full text-xs font-medium">
          {question.topic || 'General'}
        </span>
        <span className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${getDifficultyBadge()}`}>
          {question.difficulty || 'Medium'}
        </span>
      </div>

      <p className="text-lg text-gray-900 font-medium mb-6 leading-relaxed">
        {question.text}
      </p>

      <div className="space-y-3">
        {question.options.map((option, index) => {
          const isSelected = selectedOptionId === option.option_id;
          
          return (
            <button
              key={option.option_id}
              onClick={() => onSelect(option.option_id)}
              className={`
                w-full flex items-center gap-3 p-4 rounded-lg border-2 transition-all duration-150
                text-left
                ${isSelected 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300'
                }
              `}
            >
              <span className={`
                flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-semibold
                ${isSelected ? 'border-blue-500 text-blue-600' : 'border-gray-300 text-gray-600'}
              `}>
                {optionLetters[index]}
              </span>
              <span className="text-gray-700 flex-1">{option.text}</span>
            </button>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-100">
        <button
          onClick={onFlag}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-150
            ${flagged 
              ? 'bg-yellow-50 text-yellow-700' 
              : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
            }
          `}
        >
          {flagged ? (
            <BookmarkCheck className="w-4 h-4" />
          ) : (
            <Bookmark className="w-4 h-4" />
          )}
          <span>{flagged ? 'Flagged for review' : 'Flag for review'}</span>
        </button>
      </div>

      <div className="mt-4 text-xs text-gray-400 text-center">
        Press 1/A, 2/B, 3/C, or 4/D to select an option
      </div>
    </div>
  );
};

export default QuestionCard;