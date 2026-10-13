import React from "react";
import "../assets/css/Report.css";

const Report = ({ report }) => {
  const score = report?.score ?? "N/A";
  const correct_answer = report?.correct_answer ?? "N/A";
  const feedback = report?.improvment_area || [];

  return (
    <div className="report-container">
      <div className="report-header-section">
        <span className="report-badge">Official Assessment Result</span>
        <h1 className="report-header">Interview Performance Report</h1>
        <p className="report-subtitle">
          AI-generated evaluation analysis and actionable technical recommendations
        </p>
      </div>

      <div className="report-cards">
        <div className="report-card">
          <h3>Overall Score</h3>
          <div className="card-value">{score}</div>
        </div>
        <div className="report-card">
          <h3>Correct Answers</h3>
          <div className="card-value success">{correct_answer}</div>
        </div>
      </div>

      <div className="feedback-section">
        <h3>🎯 Detailed Technical Feedback & Improvement Areas</h3>
        <ul className="feedback-list">
          {Array.isArray(feedback) && feedback.length > 0 ? (
            feedback.map((point, index) => (
              <li key={index}>{point}</li>
            ))
          ) : (
            <li>No specific improvement areas flagged. Great performance!</li>
          )}
        </ul>
      </div>

      <div className="report-completion-card">
        <span className="completion-check">✓</span>
        <div>
          <h4>Interview Completed</h4>
          <p>Your session evaluation has been safely recorded and submitted to the recruiting team.</p>
        </div>
      </div>
    </div>
  );
};

export default Report;