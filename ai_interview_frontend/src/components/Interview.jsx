import React from "react";
import "../assets/css/Interview.css";
import speaking from "../assets/images/speaking.gif";
import listening from "../assets/images/listening.gif";
import { APP_CONSTANT } from "../util/constant";
import QuestionCard from "./QuestionCard";

const Interview = ({
  question,
  state,
  isFollowUp,
  followUpNum,
  baseNum,
  totalBase,
  aiThinking,
  skipQuestion,
  endInterview,
  doneSpeaking,
  transcript,
  micError,
}) => {
  return (
    <div className="interview-page-wrapper">
      <div className="interview-top-bar">
        <div className="studio-brand-group">
          <span className="studio-brand-pill">LIVE SESSION</span>
          <span className="studio-brand-name">AI Interview Studio</span>
        </div>
        <div className="studio-status-indicator">
          <span className="live-pulse-dot"></span>
          <span>Voice Channel Active</span>
        </div>
      </div>

      {micError && <div className="mic-error-banner">{micError}</div>}

      <QuestionCard
        question={question}
        state={state}
        isFollowUp={isFollowUp}
        followUpNum={followUpNum}
        baseNum={baseNum}
        totalBase={totalBase}
        aiThinking={aiThinking}
      />

      <div className="interview-container">
        {/* Col1: AI Bot */}
        <div className="interview-column">
          <div className="bot-section">
            <h2>🤖 AI Interviewer</h2>
            {state === APP_CONSTANT.ASKING ? (
              <div className="gif-placeholder">
                <img src={speaking} alt="Bot Speaking..." />
              </div>
            ) : (
              <div className="gif-placeholder-gray"></div>
            )}
            <p className="state-indicator">
              {aiThinking
                ? "Analyzing answer..."
                : state === APP_CONSTANT.ASKING
                ? "Speaking question..."
                : "Waiting for your answer"}
            </p>
          </div>
        </div>

        {/* Col2: Controls */}
        <div className="interview-column controls-section">
          {state === APP_CONSTANT.LISTENING && !aiThinking && (
            <button onClick={doneSpeaking} className="control-btn done-btn">
              ✓ Done Speaking (Submit)
            </button>
          )}
          <button
            onClick={skipQuestion}
            className="control-btn skip-btn"
            disabled={aiThinking}
          >
            Skip Question
          </button>
          <button
            onClick={endInterview}
            className="control-btn end-btn"
            disabled={aiThinking}
          >
            End Interview
          </button>
        </div>

        {/* Col3: Candidate Audio / Transcription */}
        <div className="interview-column">
          <div className="candidate-section">
            <h2>👤 You (Candidate)</h2>
            {state === APP_CONSTANT.LISTENING && !aiThinking ? (
              <div className="gif-placeholder">
                <img src={listening} alt="Listening..." />
              </div>
            ) : (
              <div className="gif-placeholder-gray"></div>
            )}
            {state === APP_CONSTANT.LISTENING && (
              <div className="transcript-box">
                <div className="transcript-header">What the AI is hearing:</div>
                <div className="transcript-content">
                  {transcript || "Listening... speak now"}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Interview;