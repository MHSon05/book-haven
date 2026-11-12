import { useState, useEffect, useCallback, useRef } from 'react';

const ERROR_MESSAGES = {
  'not-allowed': 'Vui lòng cấp quyền truy cập Micro trên trình duyệt để sử dụng tìm kiếm giọng nói.',
  'no-speech': 'Không nghe thấy giọng nói. Vui lòng nói to hơn hoặc thử lại.',
  'network': 'Lỗi kết nối mạng khi xử lý giọng nói. Vui lòng kiểm tra đường truyền.',
  'audio-capture': 'Không tìm thấy thiết bị thu âm (Micro). Vui lòng kiểm tra kết nối phần cứng.',
  'aborted': 'Đã dừng thu âm giọng nói.',
};

export function useSpeechRecognition({ onResult, onError }) {
  const [isListening, setIsListening] = useState(false);
  const [hasSupport, setHasSupport] = useState(false);
  const recognitionRef = useRef(null);
  const onResultRef = useRef(onResult);
  const onErrorRef = useRef(onError);

  // Cập nhật ref mỗi khi hàm callback thay đổi mà không làm re-init recognition
  useEffect(() => {
    onResultRef.current = onResult;
  }, [onResult]);

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setHasSupport(true);
      const recognition = new SpeechRecognition();
      recognition.lang = 'vi-VN';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onresult = (event) => {
        setIsListening(false);
        const transcript = event.results?.[0]?.[0]?.transcript?.trim();
        if (transcript && onResultRef.current) {
          onResultRef.current(transcript);
        }
      };

      recognition.onerror = (event) => {
        setIsListening(false);
        const rawErr = event.error || 'unknown';
        // Bỏ qua lỗi aborted khi người dùng chủ động bấm dừng
        if (rawErr === 'aborted') return;
        const friendlyMsg = ERROR_MESSAGES[rawErr] || `Lỗi nhận diện giọng nói: ${rawErr}`;
        if (onErrorRef.current) {
          onErrorRef.current(friendlyMsg);
        }
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    } else {
      setHasSupport(false);
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
        recognitionRef.current = null;
      }
    };
  }, []);

  const startListening = useCallback(() => {
    if (!recognitionRef.current) return;
    try {
      setIsListening(true);
      recognitionRef.current.start();
    } catch {
      // nếu đã chạy thì thử stop rồi bật lại
      try {
        recognitionRef.current.stop();
      } catch {
        // ignore
      }
      setIsListening(false);
    }
  }, []);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) return;
    try {
      recognitionRef.current.stop();
    } catch {
      // ignore
    }
    setIsListening(false);
  }, []);

  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  return {
    isListening,
    hasSupport,
    startListening,
    stopListening,
    toggleListening,
  };
}
