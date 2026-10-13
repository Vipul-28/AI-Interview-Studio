import React, { useState, useEffect, useCallback, useRef } from "react";
import { useParams } from "react-router-dom";
import { getCandidateSessionAPI } from "../services/candidate";
import { useSpeechToText } from "../hooks/useSpeechToText";
import { useInterviewWebSocket } from "../hooks/useInterviewWebSocket";
import { APP_CONSTANT } from "../util/constant";
import { playAudio } from "../util/audio";
import Interview from "../components/Interview";
import Report from "../components/Report";
import "../assets/css/CandidatePage.css";

const CandidatePage = () => {
  const { sessionId } = useParams();

  const [sessionInfo, setSessionInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isStarted, setIsStarted] = useState(false);

  const [status, setStatus] = useState(APP_CONSTANT.IDLE);
  const [report, setReport] = useState(null);

  const prevQuestionRef = useRef("");

  const {
    transcript,
    micError,
    startListening,
    stopListening,
    getTranscript,
  } = useSpeechToText();

  // Load invitation session info on mount
  useEffect(() => {
    const loadSession = async () => {
      setLoading(true);
      try {
        const data = await getCandidateSessionAPI(sessionId);
        if (!data) {
          setError("Interview invitation not found. Please verify your link.");
        } else {
          setSessionInfo(data);
        }
      } catch (e) {
        setError("Unable to load interview details. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    loadSession();
  }, [sessionId]);

  // WebSocket callbacks
  const handleWebSocketInit = useCallback((data) => {
    setStatus(APP_CONSTANT.INTRO);
    const introText = data.introText || "Welcome to your technical interview.";
    playAudio(introText, () => {
      setStatus(APP_CONSTANT.ASKING);
    });
  }, []);

  const handleReportReceived = useCallback((reportData) => {
    stopListening();
    setReport(reportData);
    setStatus(APP_CONSTANT.COMPLETED);
  }, [stopListening]);

  // Active WebSocket hook (only active after isStarted = true)
  const activeSessionId = isStarted ? sessionId : null;
  const {
    currentQuestion,
    isFollowUp,
    followUpNum,
    baseNum,
    totalBase,
    aiThinking,
    wsError,
    sendAnswer,
    skipQuestion: wsSkipQuestion,
    endInterview: wsEndInterview,
  } = useInterviewWebSocket(activeSessionId, handleWebSocketInit, handleReportReceived);

  // Play audio when question arrives
  useEffect(() => {
    if (
      status === APP_CONSTANT.ASKING &&
      currentQuestion &&
      currentQuestion !== prevQuestionRef.current
    ) {
      prevQuestionRef.current = currentQuestion;

      playAudio(currentQuestion, () => {
        setTimeout(() => {
          setStatus(APP_CONSTANT.LISTENING);
          startListening();
        }, 600);
      });
    }
  }, [status, currentQuestion, startListening]);

  // Check microphone permission before entering studio
  const handleStartInterview = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Your browser does not support microphone access. Please use Chrome or Edge.");
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
    } catch (e) {
      setError("🎤 Microphone access is required. Please allow microphone permission in your browser to proceed.");
      return;
    }

    setError("");
    setIsStarted(true);
  };

  const handleDoneSpeaking = () => {
    stopListening();
    const text = getTranscript() || transcript;
    setStatus(APP_CONSTANT.ASKING);
    sendAnswer(text || "");
  };

  const handleSkipQuestion = () => {
    stopListening();
    setStatus(APP_CONSTANT.ASKING);
    wsSkipQuestion();
  };

  const handleEndInterview = () => {
    stopListening();
    const text = getTranscript() || transcript;
    if (text && text.trim()) {
      sendAnswer(text.trim());
    }
    wsEndInterview();
  };

  if (loading) {
    return (
      <div className="candidate-portal-wrapper">
        <div className="invitation-card">
          <p style={{ color: "#38bdf8" }}>Loading your interview invitation...</p>
        </div>
      </div>
    );
  }

  if (error && !isStarted) {
    return (
      <div className="candidate-portal-wrapper">
        <div className="invitation-card">
          <h2 style={{ color: "#f87171" }}>Notice</h2>
          <p style={{ color: "#cbd5e1" }}>{error}</p>
        </div>
      </div>
    );
  }

  if (sessionInfo?.has_completed && !report) {
    return (
      <div className="candidate-portal-wrapper">
        <div className="invitation-card">
          <span className="company-tag">Interview Completed</span>
          <h2 style={{ color: "#4ade80" }}>Thank you, {sessionInfo.candidate_name}!</h2>
          <p style={{ color: "#cbd5e1", lineHeight: "1.6" }}>
            You have already completed your interview for <strong>{sessionInfo.job_title}</strong>.
            Your evaluation has been submitted to the recruiting team.
          </p>
        </div>
      </div>
    );
  }

  // Pre-interview Welcome Screen
  if (!isStarted) {
    return (
      <div className="candidate-portal-wrapper">
        <div className="invitation-card">
          <span className="company-tag">Official Technical Interview</span>
          <h2 className="candidate-welcome-title">
            Welcome, {sessionInfo?.candidate_name}!
          </h2>
          <p style={{ color: "#94a3b8", margin: 0 }}>
            You have been invited to complete a live AI-powered technical interview.
          </p>

          <div className="role-badge-box">
            Target Role: <strong>{sessionInfo?.job_title}</strong>
          </div>

          <div className="instructions-grid">
            {sessionInfo?.github_url && (
              <div className="instruction-item" style={{ gridColumn: "1 / -1" }}>
                <span>🔗</span>
                <span>GitHub Repository: <strong style={{ color: "#38bdf8" }}>{sessionInfo.github_url}</strong></span>
              </div>
            )}
            <div className="instruction-item">
              <span>🎙️</span>
              <span>Microphone required for voice responses</span>
            </div>
            <div className="instruction-item">
              <span>🤖</span>
              <span>Dynamic AI follow-ups based on your answers</span>
            </div>
            <div className="instruction-item">
              <span>⏱️</span>
              <span>Duration: Approx. 10–15 minutes</span>
            </div>
            <div className="instruction-item">
              <span>🎧</span>
              <span>Quiet environment recommended</span>
            </div>
          </div>

          <button className="start-studio-btn" onClick={handleStartInterview}>
            Check Microphone & Enter Interview Studio
          </button>
        </div>
      </div>
    );
  }

  // Completed State
  if (status === APP_CONSTANT.COMPLETED) {
    return <Report report={report} />;
  }

  // Active Interview Studio
  return (
    <>
      {wsError && (
        <div className="mic-error-banner" style={{ margin: "16px" }}>
          ⚠️ {wsError}
        </div>
      )}

      <Interview
        question={currentQuestion}
        state={status}
        isFollowUp={isFollowUp}
        followUpNum={followUpNum}
        baseNum={baseNum}
        totalBase={totalBase}
        aiThinking={aiThinking}
        skipQuestion={handleSkipQuestion}
        endInterview={handleEndInterview}
        doneSpeaking={handleDoneSpeaking}
        transcript={transcript}
        micError={micError}
      />
    </>
  );
};

export default CandidatePage;
