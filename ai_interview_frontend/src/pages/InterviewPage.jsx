import { useEffect, useState, useCallback, useRef } from "react";
import { APP_CONSTANT } from "../util/constant";
import StartInterview from "../components/StartInterview";
import Interview from "../components/Interview";
import Report from "../components/Report";
import { playAudio } from "../util/audio";
import { useSpeechToText } from "../hooks/useSpeechToText";
import { useInterviewWebSocket } from "../hooks/useInterviewWebSocket";
import "../assets/css/InterviewPage.css";

const InterviewPage = () => {
  const [sessionId, setSessionId] = useState(null);
  const [status, setStatus] = useState(APP_CONSTANT.IDLE);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const prevQuestionRef = useRef("");

  const {
    transcript,
    micError,
    startListening,
    stopListening,
    getTranscript,
  } = useSpeechToText();

  // Callback when initial WebSocket handshake finishes
  const handleWebSocketInit = useCallback((data) => {
    setLoading(false);
    setStatus(APP_CONSTANT.INTRO);

    const introText = data.introText || "Welcome to your mock interview.";
    playAudio(introText, () => {
      setStatus(APP_CONSTANT.ASKING);
    });
  }, []);

  // Callback when final graded report arrives over WebSocket
  const handleReportReceived = useCallback((reportData) => {
    stopListening();
    setReport(reportData);
    setStatus(APP_CONSTANT.COMPLETED);
    setLoading(false);
  }, [stopListening]);

  // Hook managing the WebSocket connection and state
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
  } = useInterviewWebSocket(sessionId, handleWebSocketInit, handleReportReceived);

  // Play question audio whenever a new question is assigned
  useEffect(() => {
    if (
      status === APP_CONSTANT.ASKING &&
      currentQuestion &&
      currentQuestion !== prevQuestionRef.current
    ) {
      prevQuestionRef.current = currentQuestion;

      playAudio(currentQuestion, () => {
        // Short buffer to let speaker audio settle before turning on microphone
        setTimeout(() => {
          setStatus(APP_CONSTANT.LISTENING);
          startListening();
        }, 600);
      });
    }
  }, [status, currentQuestion, startListening]);

  // Handle manual answer submission via green button
  const handleDoneSpeaking = async () => {
    stopListening();
    const text = getTranscript() || transcript;
    setStatus(APP_CONSTANT.ASKING);
    sendAnswer(text || "");
  };

  // Handle skipping the current question
  const handleSkipQuestion = () => {
    stopListening();
    setStatus(APP_CONSTANT.ASKING);
    wsSkipQuestion();
  };

  // Handle ending the interview early
  const handleEndInterview = () => {
    stopListening();
    const currentAnswer = getTranscript() || transcript;
    setLoading(true);
    // If candidate spoke something before clicking End, pass it as final answer
    if (currentAnswer && currentAnswer.trim()) {
      sendAnswer(currentAnswer.trim());
    }
    wsEndInterview();
  };

  // Called when initial form (PDF upload) finishes and creates a session
  const handleStartSession = (data, createdSessionId) => {
    setLoading(true);
    setSessionId(createdSessionId);
  };

  return (
    <>
      {loading && (
        <div className="loader-overlay">
          <div className="loader"></div>
        </div>
      )}

      {wsError && (
        <div className="mic-error-banner" style={{ margin: "16px" }}>
          ⚠️ {wsError}
        </div>
      )}

      {status === APP_CONSTANT.IDLE && (
        <StartInterview onClick={handleStartSession} />
      )}

      {(status === APP_CONSTANT.INTRO ||
        status === APP_CONSTANT.ASKING ||
        status === APP_CONSTANT.LISTENING) && (
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
      )}

      {status === APP_CONSTANT.COMPLETED && <Report report={report} />}
    </>
  );
};

export default InterviewPage;