import { useRef, useEffect } from 'react';

export default function WebcamPreview({ stream, isChecking, violations = 0 }) {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  return (
    <div className="fixed bottom-4 right-4 w-20 h-[60px] bg-gray-900 rounded-lg overflow-hidden border-2 border-gray-700">
      {stream ? (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
          <div
            className={`absolute inset-0 border-2 rounded-lg pointer-events-none transition-colors duration-200 ${
              isChecking ? 'border-red-600' : 'border-transparent'
            }`}
          />
          {violations > 0 && (
            <div className="absolute top-0 right-0 bg-red-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-bl-md">
              {violations}
            </div>
          )}
        </>
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gray-800">
          <span className="text-gray-400 text-xs font-medium">CAM OFF</span>
        </div>
      )}
    </div>
  );
}
