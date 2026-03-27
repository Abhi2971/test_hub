import { useState, useEffect, useRef } from 'react';

export default function ExamTimer({ durationMinutes, serverStartTime, onTimeUp }) {
  const [remainingSeconds, setRemainingSeconds] = useState(() => {
    const totalSeconds = durationMinutes * 60;
    const elapsed = (Date.now() - new Date(serverStartTime).getTime()) / 1000;
    return Math.max(0, totalSeconds - elapsed);
  });

  const intervalRef = useRef(null);
  const onTimeUpCalledRef = useRef(false);
  const syncIntervalRef = useRef(null);
  const driftRef = useRef(0);

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      const totalSeconds = durationMinutes * 60;
      const elapsed = (Date.now() - new Date(serverStartTime).getTime()) / 1000 - driftRef.current;
      const remaining = Math.max(0, totalSeconds - elapsed);
      setRemainingSeconds(remaining);

      if (remaining <= 0 && !onTimeUpCalledRef.current) {
        onTimeUpCalledRef.current = true;
        onTimeUp();
      }
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [durationMinutes, serverStartTime, onTimeUp]);

  useEffect(() => {
    const syncWithServer = async () => {
      try {
        const response = await fetch('/api/v1/auth/me', { method: 'GET' });
        if (response.ok) {
          const serverTime = new Date().getTime();
          const localTime = Date.now();
          driftRef.current = (localTime - serverTime) / 1000;
        }
      } catch (error) {
        console.error('Failed to sync with server:', error);
      }
    };

    syncIntervalRef.current = setInterval(syncWithServer, 60000);
    syncWithServer();

    return () => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, []);

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  const isWarning = remainingSeconds <= 300 && remainingSeconds > 0;
  const isCritical = remainingSeconds <= 60 && remainingSeconds > 0;

  return (
    <>
      <style>
        {`
          @keyframes pulse-red {
            0%, 100% {
              opacity: 1;
            }
            50% {
              opacity: 0.6;
            }
          }
          .pulse-red {
            animation: pulse-red 1s ease-in-out infinite;
          }
        `}
      </style>
      <div
        className={`font-mono text-lg font-semibold ${
          isCritical ? 'text-red-600 pulse-red' : isWarning ? 'text-orange-500' : 'text-gray-700'
        }`}
      >
        {formatTime(remainingSeconds)}
      </div>
    </>
  );
}
