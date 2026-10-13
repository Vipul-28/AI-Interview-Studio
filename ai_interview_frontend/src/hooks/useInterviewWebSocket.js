import { useState, useEffect, useCallback, useRef } from "react";
import { interviewWebSocket } from "../services/interviewWebSocket";

export const useInterviewWebSocket = (sessionId, onInterviewStart, onReportReceived) => {
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [isFollowUp, setIsFollowUp] = useState(false);
  const [followUpNum, setFollowUpNum] = useState(0);
  const [baseNum, setBaseNum] = useState(1);
  const [totalBase, setTotalBase] = useState(1);
  const [aiThinking, setAiThinking] = useState(false);
  const [wsError, setWsError] = useState("");

  const onStartRef = useRef(onInterviewStart);
  const onReportRef = useRef(onReportReceived);

  useEffect(() => {
    onStartRef.current = onInterviewStart;
    onReportRef.current = onReportReceived;
  }, [onInterviewStart, onReportReceived]);

  useEffect(() => {
    if (!sessionId) return;

    interviewWebSocket.connect(sessionId, {
      onMessage: (payload) => {
        const { type, data, message } = payload;

        switch (type) {
          case "INIT":
            setAiThinking(false);
            if (data) {
              setCurrentQuestion(data.question || "");
              setIsFollowUp(false);
              setFollowUpNum(0);
              setBaseNum(data.base_num || 1);
              setTotalBase(data.total_base || 1);

              if (onStartRef.current) {
                onStartRef.current(data);
              }
            }
            break;

          case "AI_THINKING":
            setAiThinking(true);
            break;

          case "QUESTION":
            setAiThinking(false);
            if (data) {
              setCurrentQuestion(data.question || "");
              setIsFollowUp(!!data.is_follow_up);
              setFollowUpNum(data.follow_up_num || 0);
              setBaseNum(data.base_num || 1);
              setTotalBase(data.total_base || 1);
            }
            break;

          case "REPORT":
            setAiThinking(false);
            if (data && data.report && onReportRef.current) {
              onReportRef.current(data.report);
            }
            break;

          case "ERROR":
            setAiThinking(false);
            setWsError(message || "An unexpected error occurred over WebSocket.");
            break;

          default:
            console.log("Unhandled WebSocket event:", payload);
        }
      },
      onError: (err) => {
        setAiThinking(false);
        setWsError("Unable to connect to the interview WebSocket server.");
      },
      onClose: () => {
        console.log("Interview WebSocket closed.");
      },
    });

    return () => {
      interviewWebSocket.disconnect();
    };
  }, [sessionId]);

  const sendAnswer = useCallback((answerText) => {
    setAiThinking(true);
    interviewWebSocket.sendAnswer(answerText);
  }, []);

  const skipQuestion = useCallback(() => {
    setAiThinking(true);
    interviewWebSocket.sendSkip();
  }, []);

  const endInterview = useCallback(() => {
    setAiThinking(true);
    interviewWebSocket.sendEndInterview();
  }, []);

  return {
    currentQuestion,
    isFollowUp,
    followUpNum,
    baseNum,
    totalBase,
    aiThinking,
    wsError,
    sendAnswer,
    skipQuestion,
    endInterview,
  };
};
