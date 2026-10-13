import React from "react";
import { APP_CONSTANT } from "../util/constant";

const QuestionCard = ({
  question,
  state,
  isFollowUp,
  followUpNum,
  baseNum,
  totalBase,
  aiThinking
}) => {
  return (
    <div className="question-banner-card">
      <div className="question-meta-row">
        <span className="question-tag base-tag">
          Topic {baseNum} of {totalBase}
        </span>
        {isFollowUp ? (
          <span className="question-tag followup-tag">
            🔍 Dynamic Follow-up {followUpNum} of 2
          </span>
        ) : (
          <span className="question-tag primary-tag">
            📌 Primary Question
          </span>
        )}
      </div>

      <h3 className="question-title">
        {question || "Preparing your question..."}
      </h3>

      <div className="status-row">
        {aiThinking ? (
          <div className="status-pill status-thinking">
            ⚡ AI is evaluating your response and preparing next question...
          </div>
        ) : state === APP_CONSTANT.ASKING ? (
          <div className="status-pill status-asking">
            🤖 AI Interviewer is speaking...
          </div>
        ) : (
          <div className="status-pill status-listening">
            🎙️ Microphone is active — listening to your answer
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionCard;
