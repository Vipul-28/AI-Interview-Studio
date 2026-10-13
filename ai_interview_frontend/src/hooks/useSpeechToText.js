import { useEffect, useRef, useState } from "react";

export const useSpeechToText = () => {
  const recognitionRef = useRef(null);
  const isListeningRef = useRef(false);
  const transcriptRef = useRef("");
  const [transcript, setTranscript] = useState("");
  const [micError, setMicError] = useState("");

  useEffect(() => {
    transcriptRef.current = transcript;
  }, [transcript]);

  const resetTranscript = () => {
    setTranscript("");
    transcriptRef.current = "";
  };

  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.error("SpeechRecognition is not supported");
      setMicError("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
      return;
    }

    // Stop any existing instance
    if (recognitionRef.current) {
      try {
        isListeningRef.current = false;
        recognitionRef.current.stop();
      } catch (e) {
        // ignore
      }
    }

    resetTranscript();
    setMicError("");
    isListeningRef.current = true;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.lang = "en-US";
    recognition.interimResults = true;

    recognition.onresult = (event) => {
      let currentFullText = "";

      for (let i = 0; i < event.results.length; i++) {
        currentFullText += event.results[i][0].transcript + " ";
      }

      currentFullText = currentFullText.trim();
      setTranscript(currentFullText);
      transcriptRef.current = currentFullText;
    };

    recognition.onerror = (event) => {
      console.error("SpeechRecognition error", event);
      if (event.error === "not-allowed") {
        setMicError("🎤 Microphone access denied. Please allow microphone in your browser settings and reload the page.");
      } else if (event.error === "no-speech") {
        // Normal when user pauses, do not treat as error
      } else {
        setMicError(`Microphone notice: ${event.error}`);
      }
    };

    // Auto-restart if browser stops recognition while still in listening state
    recognition.onend = () => {
      if (isListeningRef.current) {
        try {
          recognition.start();
        } catch (e) {
          // ignore if already starting
        }
      }
    };

    try {
      recognition.start();
    } catch (e) {
      console.error("SpeechRecognition start error", e);
    }
    recognitionRef.current = recognition;
  };

  const stopListening = () => {
    isListeningRef.current = false;
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        // ignore
      }
    }
  };

  return {
    transcript,
    micError,
    stopListening,
    resetTranscript,
    startListening,
    getTranscript: () => transcriptRef.current,
  };
};
