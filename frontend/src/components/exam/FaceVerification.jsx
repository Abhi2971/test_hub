import React, { useRef, useEffect } from 'react';

async function loadModels() {
  const MODEL_URL = '/face-api-models';
  await Promise.all([
    faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL),
    faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
    faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL)
  ]);
}

function FaceVerification({ stream, isActive, onViolation }) {
  const modelLoaded = useRef(false);
  const baselineDescriptor = useRef(null);
  const checkIntervalRef = useRef(null);
  const videoRef = useRef(null);

  const enrollFace = async (videoElement) => {
    if (!modelLoaded.current) {
      await loadModels();
      modelLoaded.current = true;
    }

    const descriptors = [];
    
    for (let i = 0; i < 3; i++) {
      const detection = await faceapi
        .detectSingleFace(videoElement, new faceapi.SsdMobilenetv1Options({ minConfidence: 0.5 }))
        .withFaceLandmarks()
        .withFaceDescriptor();

      if (detection) {
        descriptors.push(detection.descriptor);
      }

      if (i < 2) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }

    if (descriptors.length > 0) {
      const avgDescriptor = new Float32Array(128);
      for (let i = 0; i < 128; i++) {
        let sum = 0;
        for (let j = 0; j < descriptors.length; j++) {
          sum += descriptors[j][i];
        }
        avgDescriptor[i] = sum / descriptors.length;
      }
      baselineDescriptor.current = avgDescriptor;
      console.log('Face baseline enrolled');
    }
  };

  const performCheck = async () => {
    if (!videoRef.current || !baselineDescriptor.current) {
      return;
    }

    const detection = await faceapi
      .detectSingleFace(videoRef.current, new faceapi.SsdMobilenetv1Options({ minConfidence: 0.5 }))
      .withFaceLandmarks()
      .withFaceDescriptor();

    if (!detection) {
      onViolation('face_absent');
      return;
    }

    const currentDescriptor = detection.descriptor;
    const baseline = baselineDescriptor.current;
    
    let sumSquaredDiff = 0;
    for (let i = 0; i < currentDescriptor.length; i++) {
      const diff = currentDescriptor[i] - baseline[i];
      sumSquaredDiff += diff * diff;
    }
    const euclideanDistance = Math.sqrt(sumSquaredDiff);

    if (euclideanDistance > 0.6) {
      onViolation('face_mismatch');
    }
  };

  const scheduleNextCheck = () => {
    const randomInterval = (Math.random() * 3 + 2) * 60000;
    checkIntervalRef.current = setTimeout(() => {
      if (isActive && baselineDescriptor.current) {
        performCheck().then(() => {
          scheduleNextCheck();
        });
      }
    }, randomInterval);
  };

  useEffect(() => {
    if (stream && isActive) {
      const video = document.createElement('video');
      video.srcObject = stream;
      video.autoplay = true;
      video.playsInline = true;
      video.muted = true;
      videoRef.current = video;

      video.onloadedmetadata = () => {
        video.play().then(() => {
          enrollFace(video);
          scheduleNextCheck();
        });
      };
    }

    return () => {
      if (checkIntervalRef.current) {
        clearTimeout(checkIntervalRef.current);
      }
    };
  }, [stream, isActive]);

  useEffect(() => {
    return () => {
      if (checkIntervalRef.current) {
        clearTimeout(checkIntervalRef.current);
      }
    };
  }, []);

  return null;
}

export default FaceVerification;