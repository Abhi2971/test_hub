import { useReducer, useRef, useCallback, useEffect } from 'react';
import { attemptService } from '../services/attemptService';
import api from '../services/api';

const initialState = {
  phase: 'lobby',
  attemptId: null,
  questions: [],
  currentIndex: 0,
  answers: {},
  violations: [],
  tabSwitchCount: 0,
  examConfig: null,
  serverStartTime: null,
  result: null,
  error: null,
  saveStatus: 'idle',
  violationOverlay: null,
};

function examReducer(state, action) {
  switch (action.type) {
    case 'SET_PHASE':
      return { ...state, phase: action.payload };

    case 'SET_ATTEMPT':
      return {
        ...state,
        attemptId: action.payload.attemptId,
        questions: action.payload.questions,
        examConfig: action.payload.examConfig,
        serverStartTime: action.payload.serverStartTime,
        phase: 'in_progress',
        currentIndex: 0,
        answers: {},
        violations: [],
        tabSwitchCount: 0,
      };

    case 'SET_ANSWER': {
      const { questionId, optionId } = action.payload;
      return {
        ...state,
        answers: {
          ...state.answers,
          [questionId]: {
            ...(state.answers[questionId] || { selectedOptionId: null, flagged: false, timeSpentSeconds: 0 }),
            selectedOptionId: optionId,
          },
        },
      };
    }

    case 'TOGGLE_FLAG': {
      const { questionId } = action.payload;
      return {
        ...state,
        answers: {
          ...state.answers,
          [questionId]: {
            ...(state.answers[questionId] || { selectedOptionId: null, flagged: false, timeSpentSeconds: 0 }),
            flagged: !(state.answers[questionId]?.flagged || false),
          },
        },
      };
    }

    case 'SET_CURRENT_INDEX':
      return { ...state, currentIndex: action.payload };

    case 'ADD_VIOLATION':
      return {
        ...state,
        violations: [...state.violations, action.payload],
        tabSwitchCount: action.payload.type === 'tab_switch'
          ? state.tabSwitchCount + 1
          : state.tabSwitchCount,
      };

    case 'SET_RESULT':
      return { ...state, result: action.payload, phase: 'submitted' };

    case 'SET_ERROR':
      return { ...state, error: action.payload };

    case 'CLEAR_ERROR':
      return { ...state, error: null };

    case 'SET_SAVE_STATUS':
      return { ...state, saveStatus: action.payload };

    case 'SHOW_VIOLATION_OVERLAY':
      return { ...state, violationOverlay: action.payload };

    case 'HIDE_VIOLATION_OVERLAY':
      return { ...state, violationOverlay: null };

    case 'LOAD_BACKUP':
      return { ...state, answers: action.payload };

    default:
      return state;
  }
}

export default function useExam(exam, onViolation, onAutoSubmit) {
  const [state, dispatch] = useReducer(examReducer, initialState);
  const lastSavedAnswersRef = useRef({});
  const autoSaveTimerRef = useRef(null);
  const timeTrackingRef = useRef({});

  const startExam = useCallback(async (accessMethod, passcode) => {
    dispatch({ type: 'SET_PHASE', payload: 'starting' });
    try {
      const result = await attemptService.startAttempt(exam._id, accessMethod, passcode);
      const { attempt_id, questions, exam_config, server_time_iso } = result.data || result;

      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(() => {});
      }

      dispatch({
        type: 'SET_ATTEMPT',
        payload: {
          attemptId: attempt_id,
          questions: questions || [],
          examConfig: exam_config || {},
          serverStartTime: new Date(server_time_iso),
        },
      });

      lastSavedAnswersRef.current = {};
      timeTrackingRef.current = {};
    } catch (err) {
      const errorMsg = err?.message || err?.error || 'Failed to start exam';
      dispatch({ type: 'SET_ERROR', payload: errorMsg });
      dispatch({ type: 'SET_PHASE', payload: 'lobby' });
      throw err;
    }
  }, [exam]);

  const nextQuestion = useCallback(() => {
    dispatch({
      type: 'SET_CURRENT_INDEX',
      payload: Math.min(state.currentIndex + 1, state.questions.length - 1),
    });
  }, [state.currentIndex, state.questions.length]);

  const prevQuestion = useCallback(() => {
    dispatch({
      type: 'SET_CURRENT_INDEX',
      payload: Math.max(state.currentIndex - 1, 0),
    });
  }, [state.currentIndex]);

  const goToQuestion = useCallback((index) => {
    dispatch({ type: 'SET_CURRENT_INDEX', payload: index });
  }, []);

  const selectOption = useCallback((questionId, optionId) => {
    dispatch({ type: 'SET_ANSWER', payload: { questionId, optionId } });
  }, []);

  const toggleFlag = useCallback((questionId) => {
    dispatch({ type: 'TOGGLE_FLAG', payload: { questionId } });
  }, []);

  const saveAnswers = useCallback(async () => {
    if (!state.attemptId || state.phase !== 'in_progress') return;

    const changedAnswers = {};
    for (const [qId, answer] of Object.entries(state.answers)) {
      const lastSaved = lastSavedAnswersRef.current[qId];
      if (!lastSaved || lastSaved.selectedOptionId !== answer.selectedOptionId) {
        changedAnswers[qId] = answer.selectedOptionId;
      }
    }

    if (Object.keys(changedAnswers).length === 0) return;

    dispatch({ type: 'SET_SAVE_STATUS', payload: 'saving' });

    try {
      await attemptService.saveAnswers(state.attemptId, changedAnswers);
      lastSavedAnswersRef.current = { ...lastSavedAnswersRef.current, ...changedAnswers };
      dispatch({ type: 'SET_SAVE_STATUS', payload: 'saved' });

      try {
        localStorage.setItem(
          `exam_backup_${state.attemptId}`,
          JSON.stringify({ answers: state.answers, timestamp: Date.now() })
        );
      } catch {}
    } catch {
      dispatch({ type: 'SET_SAVE_STATUS', payload: 'error' });
      try {
        localStorage.setItem(
          `exam_backup_${state.attemptId}`,
          JSON.stringify({ answers: state.answers, timestamp: Date.now() })
        );
      } catch {}
      throw new Error('Auto-save failed');
    }
  }, [state.attemptId, state.answers, state.phase]);

  const submitExam = useCallback(async (reason = 'manual') => {
    if (!state.attemptId) return;

    dispatch({ type: 'SET_PHASE', payload: 'submitting' });

    try {
      if (Object.keys(state.answers).length > 0) {
        const allAnswers = {};
        for (const [qId, answer] of Object.entries(state.answers)) {
          allAnswers[qId] = answer.selectedOptionId;
        }
        try {
          await attemptService.saveAnswers(state.attemptId, allAnswers);
        } catch {}
      }

      const result = await attemptService.submitAttempt(state.attemptId);
      const resultData = result.data || result;

      try {
        localStorage.removeItem(`exam_backup_${state.attemptId}`);
      } catch {}

      dispatch({ type: 'SET_RESULT', payload: resultData });
    } catch (err) {
      dispatch({ type: 'SET_ERROR', payload: 'Submission failed. Please try again.' });
      dispatch({ type: 'SET_PHASE', payload: 'in_progress' });
      throw err;
    }
  }, [state.attemptId, state.answers]);

  const logViolation = useCallback(async (type) => {
    if (!state.attemptId) return;

    const violation = { type, timestamp: new Date().toISOString() };

    try {
      const response = await attemptService.logViolation(state.attemptId, type);
      if (response?.action === 'auto_submitted') {
        await submitExam('violation');
        return;
      }
    } catch {}

    dispatch({ type: 'ADD_VIOLATION', payload: violation });

    if (type === 'tab_switch') {
      const newCount = state.tabSwitchCount + 1;
      const limit = exam?.security?.tab_switch_limit || 999;

      dispatch({
        type: 'SHOW_VIOLATION_OVERLAY',
        payload: { type: 'tab_switch', count: newCount, limit },
      });

      if (newCount >= limit) {
        onAutoSubmit?.();
      }

      onViolation?.(type, newCount, limit);
    } else if (type === 'fullscreen_exit') {
      dispatch({
        type: 'SHOW_VIOLATION_OVERLAY',
        payload: { type: 'fullscreen_exit' },
      });
      onViolation?.(type);
    } else if (type === 'copy_paste') {
      dispatch({
        type: 'SHOW_VIOLATION_OVERLAY',
        payload: { type: 'copy_paste' },
      });
      onViolation?.(type);
    }
  }, [state.attemptId, state.tabSwitchCount, exam, submitExam, onViolation, onAutoSubmit]);

  const dismissViolationOverlay = useCallback(() => {
    dispatch({ type: 'HIDE_VIOLATION_OVERLAY' });
  }, []);

  const returnToFullscreen = useCallback(() => {
    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(() => {});
    }
    dispatch({ type: 'HIDE_VIOLATION_OVERLAY' });
  }, []);

  const restoreFromBackup = useCallback(() => {
    if (!state.attemptId) return;
    try {
      const backup = localStorage.getItem(`exam_backup_${state.attemptId}`);
      if (backup) {
        const { answers } = JSON.parse(backup);
        dispatch({ type: 'LOAD_BACKUP', payload: answers });
      }
    } catch {}
  }, [state.attemptId]);

  const startAutoSave = useCallback(() => {
    if (autoSaveTimerRef.current) {
      clearInterval(autoSaveTimerRef.current);
    }
    autoSaveTimerRef.current = setInterval(() => {
      saveAnswers().catch(() => {});
    }, 30000);
  }, [saveAnswers]);

  const stopAutoSave = useCallback(() => {
    if (autoSaveTimerRef.current) {
      clearInterval(autoSaveTimerRef.current);
      autoSaveTimerRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => {
      stopAutoSave();
    };
  }, [stopAutoSave]);

  const syncServerTime = useCallback(async () => {
    try {
      const response = await api.get('/auth/me');
      return new Date(response.data?.server_time || new Date());
    } catch {
      return null;
    }
  }, []);

  const answeredCount = Object.values(state.answers).filter(
    (a) => a?.selectedOptionId
  ).length;

  const currentQuestion = state.questions[state.currentIndex];
  const currentAnswer = currentQuestion
    ? state.answers[currentQuestion.id]
    : null;

  return {
    state,
    dispatch,
    actions: {
      startExam,
      nextQuestion,
      prevQuestion,
      goToQuestion,
      selectOption,
      toggleFlag,
      saveAnswers,
      submitExam,
      logViolation,
      dismissViolationOverlay,
      returnToFullscreen,
      restoreFromBackup,
      startAutoSave,
      stopAutoSave,
      syncServerTime,
    },
    derived: {
      answeredCount,
      currentQuestion,
      currentAnswer,
      totalQuestions: state.questions.length,
      isLastQuestion: state.currentIndex === state.questions.length - 1,
      isFirstQuestion: state.currentIndex === 0,
    },
  };
}
