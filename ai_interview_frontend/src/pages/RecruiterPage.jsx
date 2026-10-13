import React, { useState, useEffect } from "react";
import {
  createInterviewAPI,
  getInterviewsAPI,
  getInterviewDetailAPI,
  resendInviteAPI,
  sendReportEmailAPI,
} from "../services/recruiter";
import { ROLE_PRESETS } from "../util/rolePresets";
import "../assets/css/RecruiterPage.css";

const RecruiterPage = () => {
  const [activeTab, setActiveTab] = useState("create"); // 'create' | 'sessions'
  const [selectedRoleId, setSelectedRoleId] = useState(ROLE_PRESETS[0].id);
  const [jobTitle, setJobTitle] = useState(ROLE_PRESETS[0].title);
  const [jobDescription, setJobDescription] = useState(ROLE_PRESETS[0].description);
  const [candidateName, setCandidateName] = useState("");
  const [candidateEmail, setCandidateEmail] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [resumeFile, setResumeFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [createdSession, setCreatedSession] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);

  const [sessions, setSessions] = useState([]);
  const [selectedSessionDetail, setSelectedSessionDetail] = useState(null);

  useEffect(() => {
    if (activeTab === "sessions") {
      loadSessions();
    }
  }, [activeTab]);

  const loadSessions = async () => {
    try {
      const data = await getInterviewsAPI();
      setSessions(data || []);
    } catch (e) {
      console.error("Failed to load sessions:", e);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== "application/pdf") {
        setError("Only PDF resumes are supported.");
        return;
      }
      setError("");
      setResumeFile(file);
    }
  };

  const handleSelectRole = (preset) => {
    setSelectedRoleId(preset.id);
    if (preset.id === "custom") {
      setJobTitle("");
      setJobDescription("");
    } else {
      setJobTitle(preset.title);
      setJobDescription(preset.description);
    }
  };

  const isSoftwareRole =
    selectedRoleId === "software_engineer" ||
    selectedRoleId === "data_scientist" ||
    selectedRoleId === "devops_engineer" ||
    selectedRoleId === "custom" ||
    /software|engineer|developer|frontend|backend|fullstack|devops|data|coding|tech|architect/i.test(jobTitle);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jobTitle || !jobDescription || !resumeFile) {
      setError("Job Title, Job Description, and Resume PDF are required.");
      return;
    }

    setLoading(true);
    setError("");
    setCreatedSession(null);

    try {
      const formData = new FormData();
      formData.append("job_title", jobTitle);
      formData.append("job_description", jobDescription);
      formData.append("candidate_name", candidateName || "Candidate");
      if (candidateEmail) formData.append("candidate_email", candidateEmail);
      if (githubUrl && githubUrl.trim()) formData.append("github_url", githubUrl.trim());
      formData.append("resume", resumeFile);

      const result = await createInterviewAPI(formData);
      setCreatedSession(result);
    } catch (err) {
      console.error(err);
      setError("Failed to create interview. Please check your backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const candidateLink = createdSession
    ? `${window.location.origin}/candidate/${createdSession.session_id}`
    : "";

  const handleCopyLink = () => {
    if (candidateLink) {
      navigator.clipboard.writeText(candidateLink);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2500);
    }
  };

  const handleResendInvite = async (sessionId) => {
    try {
      const res = await resendInviteAPI(sessionId);
      alert(res.message || "Invitation email sent!");
    } catch (e) {
      alert("Failed to send invite email. Check SMTP settings.");
    }
  };

  const handleSendReportEmail = async (sessionId) => {
    try {
      const res = await sendReportEmailAPI(sessionId);
      alert(res.message || "Report email sent!");
    } catch (e) {
      alert("Failed to send report email. Check SMTP settings.");
    }
  };

  const viewSessionDetail = async (sessionId) => {
    const detail = await getInterviewDetailAPI(sessionId);
    setSelectedSessionDetail(detail);
  };

  return (
    <div className="recruiter-container">
      <div className="recruiter-header">
        <span className="recruiter-badge">Enterprise Admin Portal</span>
        <h1 className="recruiter-title">AI Interview Studio</h1>
        <p className="recruiter-subtitle">
          Recruiter Portal: configure criteria, upload candidate resumes, and dispatch live interview links.
        </p>
      </div>

      <div className="recruiter-tabs">
        <button
          className={`tab-btn ${activeTab === "create" ? "active" : ""}`}
          onClick={() => setActiveTab("create")}
        >
          + Create Interview Invitation
        </button>
        <button
          className={`tab-btn ${activeTab === "sessions" ? "active" : ""}`}
          onClick={() => setActiveTab("sessions")}
        >
          📋 Candidate Sessions ({sessions.length})
        </button>
        <a
          href="/practice"
          className="tab-btn"
          style={{ marginLeft: "auto", textDecoration: "none", display: "inline-flex", alignItems: "center" }}
        >
          🎙️ Open Practice Studio
        </a>
      </div>

      {activeTab === "create" && (
        <div className="recruiter-card">
          <form onSubmit={handleSubmit}>
            {error && <div className="mic-error-banner">{error}</div>}

            {/* Role Preset Chips Selector */}
            <div className="role-preset-selector">
              <span className="section-label">Select Interview Role Category</span>
              <div className="role-chips-grid">
                {ROLE_PRESETS.map((preset) => (
                  <button
                    key={preset.id}
                    type="button"
                    className={`role-chip ${selectedRoleId === preset.id ? "active" : ""}`}
                    onClick={() => handleSelectRole(preset)}
                  >
                    <span className="role-icon">{preset.icon}</span>
                    <span>{preset.title}</span>
                  </button>
                ))}
              </div>
            </div>

            {selectedRoleId === "custom" && (
              <div className="custom-role-banner">
                <span className="banner-icon">💡</span>
                <div>
                  <strong>Custom Role Mode:</strong> You can create an interview for ANY industry or specialized job title outside our presets (e.g. Cybersecurity, QA Lead, Solutions Architect). Enter your role name and requirements below.
                </div>
              </div>
            )}

            <div className="form-grid">
              <div className="form-field">
                <label>
                  {selectedRoleId === "custom" ? "Custom Role Name" : "Job Title"}
                </label>
                <input
                  type="text"
                  placeholder={
                    selectedRoleId === "custom"
                      ? "e.g. Cybersecurity Analyst, QA Automation Lead, Solutions Architect"
                      : "e.g. Senior Full Stack Engineer"
                  }
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  required
                />
              </div>

              <div className="form-field">
                <label>Candidate Name</label>
                <input
                  type="text"
                  placeholder="e.g. Alex Johnson"
                  value={candidateName}
                  onChange={(e) => setCandidateName(e.target.value)}
                />
              </div>

              <div className="form-field full-width">
                <label>Candidate Email (Optional)</label>
                <input
                  type="email"
                  placeholder="e.g. alex.johnson@example.com"
                  value={candidateEmail}
                  onChange={(e) => setCandidateEmail(e.target.value)}
                />
              </div>

              {/* Dynamic GitHub Link for Software / Tech Roles */}
              {isSoftwareRole && (
                <div className="form-field full-width github-field-box">
                  <div className="github-label-row">
                    <label style={{ margin: 0 }}>Candidate GitHub Repository or Profile URL (Optional)</label>
                    <span className="github-tag">Code Context Powered</span>
                  </div>
                  <input
                    type="url"
                    placeholder="e.g. https://github.com/username or https://github.com/username/project-repo"
                    value={githubUrl}
                    onChange={(e) => setGithubUrl(e.target.value)}
                  />
                  <p className="field-hint">
                    🔗 <strong>Smart Code Cross-Referencing:</strong> The AI inspects the candidate's GitHub repositories against your Job Description requirements. If a project in their repo matches the required skills (e.g., Python, React, Docker, APIs), a targeted interview question will be generated directly about their actual implementation!
                  </p>
                </div>
              )}

              <div className="form-field full-width">
                <label>Job Description</label>
                <textarea
                  placeholder="Paste the role requirements, required skills, and core responsibilities..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  required
                />
              </div>

              <div className="form-field full-width">
                <label>Candidate Resume (PDF)</label>
                <label className="upload-zone">
                  <input type="file" accept=".pdf" onChange={handleFileChange} />
                  <span>
                    {resumeFile
                      ? `📄 Selected: ${resumeFile.name}`
                      : "📁 Click to upload Candidate PDF Resume"}
                  </span>
                </label>
              </div>
            </div>

            <button type="submit" className="submit-btn-glow" disabled={loading}>
              {loading
                ? "⚡ Generating Questions & Preparing Candidate Session..."
                : "Generate Candidate Interview Link"}
            </button>
          </form>

          {createdSession && (
            <div className="generated-link-banner">
              <h3 style={{ margin: "0 0 8px 0", color: "#10b981" }}>
                ✓ Candidate Interview Invitation Ready!
              </h3>
              <p style={{ margin: "0 0 12px 0", color: "#cbd5e1", fontSize: "0.95rem" }}>
                Share this link with <strong>{createdSession.candidate_name}</strong>. The candidate will only see the interview studio without access to JD or file uploads.
              </p>
              <div className="link-row">
                <input type="text" readOnly value={candidateLink} className="link-input" />
                <button onClick={handleCopyLink} className="copy-btn">
                  {copySuccess ? "✓ Copied!" : "Copy Link"}
                </button>
              </div>

              {createdSession.candidate_email && (
                <div style={{ marginTop: "12px", padding: "10px 14px", background: "rgba(56, 189, 248, 0.15)", border: "1px solid rgba(56, 189, 248, 0.3)", borderRadius: "6px", color: "#38bdf8", fontSize: "0.9rem" }}>
                  ✉️ Invitation email sent directly to: <strong>{createdSession.candidate_email}</strong>
                </div>
              )}

              {createdSession.github_url && (
                <div style={{ marginTop: "10px", padding: "8px 12px", background: "rgba(15, 23, 42, 0.6)", border: "1px solid rgba(56, 189, 248, 0.3)", borderRadius: "6px", color: "#cbd5e1", fontSize: "0.85rem" }}>
                  🔗 Repository Attached: <strong style={{ color: "#38bdf8" }}>{createdSession.github_url}</strong>
                </div>
              )}

              {createdSession.questions && createdSession.questions.length > 0 && (
                <div style={{ marginTop: "16px", background: "#0f172a", padding: "14px", borderRadius: "8px" }}>
                  <strong style={{ fontSize: "0.85rem", color: "#94a3b8", textTransform: "uppercase" }}>
                    Pre-generated Base Questions:
                  </strong>
                  <ul style={{ margin: "8px 0 0 20px", color: "#e2e8f0", fontSize: "0.95rem" }}>
                    {createdSession.questions.map((q, idx) => (
                      <li key={idx}>{q}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === "sessions" && (
        <div className="recruiter-card">
          <table className="sessions-table">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Job Title</th>
                <th>Status</th>
                <th>Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sessions.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: "center", color: "#94a3b8", padding: "30px" }}>
                    No interviews created yet. Click "+ Create Interview Invitation" to get started!
                  </td>
                </tr>
              ) : (
                sessions.map((s) => (
                  <tr key={s.session_id}>
                    <td>
                      <strong>{s.candidate_name}</strong>
                    </td>
                    <td>{s.job_title}</td>
                    <td>
                      <span className={`status-badge status-${s.status}`}>
                        {s.status}
                      </span>
                    </td>
                    <td>
                      {s.score ? (
                        <strong style={{ color: "#4ade80" }}>{s.score}</strong>
                      ) : (
                        <span style={{ color: "#64748b" }}>—</span>
                      )}
                    </td>
                    <td>
                      {s.has_report && (
                        <>
                          <button
                            className="btn-small"
                            onClick={() => viewSessionDetail(s.session_id)}
                          >
                            View Report
                          </button>
                          {s.candidate_email && (
                            <button
                              className="btn-small"
                              onClick={() => handleSendReportEmail(s.session_id)}
                              style={{ color: "#4ade80", borderColor: "#22c55e" }}
                            >
                              📊 Email Report
                            </button>
                          )}
                        </>
                      )}
                      {s.candidate_email && !s.has_report && (
                        <button
                          className="btn-small"
                          onClick={() => handleResendInvite(s.session_id)}
                          style={{ color: "#facc15", borderColor: "#eab308" }}
                        >
                          📧 Email Invite
                        </button>
                      )}
                      <button
                        className="btn-small"
                        onClick={() => {
                          const link = `${window.location.origin}/candidate/${s.session_id}`;
                          navigator.clipboard.writeText(link);
                          alert("Candidate link copied to clipboard!");
                        }}
                      >
                        Copy Link
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Detail / Report Modal */}
      {selectedSessionDetail && (
        <div className="modal-overlay" onClick={() => setSelectedSessionDetail(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <h2 style={{ margin: 0 }}>Candidate Assessment Report</h2>
              <button
                className="btn-small"
                onClick={() => setSelectedSessionDetail(null)}
                style={{ fontSize: "1.1rem" }}
              >
                ✕
              </button>
            </div>

            <p style={{ color: "#94a3b8", margin: "0 0 12px 0" }}>
              Candidate: <strong>{selectedSessionDetail.candidate_name}</strong> | Role:{" "}
              <strong>{selectedSessionDetail.job_title}</strong>
            </p>

            {selectedSessionDetail.github_url && (
              <div style={{ margin: "0 0 16px 0", padding: "8px 12px", background: "#0f172a", borderRadius: "8px", fontSize: "0.88rem" }}>
                <span style={{ color: "#94a3b8" }}>🔗 Candidate GitHub Repository: </span>
                <a
                  href={selectedSessionDetail.github_url}
                  target="_blank"
                  rel="noreferrer"
                  style={{ color: "#38bdf8", textDecoration: "underline", wordBreak: "break-all" }}
                >
                  {selectedSessionDetail.github_url}
                </a>
              </div>
            )}

            {selectedSessionDetail.report ? (
              <div style={{ background: "#0f172a", padding: "20px", borderRadius: "10px", marginBottom: "20px" }}>
                <div style={{ display: "flex", gap: "20px", marginBottom: "16px" }}>
                  <div style={{ flex: 1, background: "#1e293b", padding: "12px", borderRadius: "8px", textAlign: "center" }}>
                    <div style={{ fontSize: "0.8rem", color: "#94a3b8" }}>OVERALL SCORE</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: "700", color: "#38bdf8" }}>
                      {selectedSessionDetail.report.score}
                    </div>
                  </div>
                  <div style={{ flex: 1, background: "#1e293b", padding: "12px", borderRadius: "8px", textAlign: "center" }}>
                    <div style={{ fontSize: "0.8rem", color: "#94a3b8" }}>CORRECT ANSWERS</div>
                    <div style={{ fontSize: "1.8rem", fontWeight: "700", color: "#4ade80" }}>
                      {selectedSessionDetail.report.correct_answer}
                    </div>
                  </div>
                </div>

                <h4 style={{ margin: "0 0 8px 0", color: "#f8fafc" }}>Detailed Technical Feedback:</h4>
                <ul style={{ margin: "0 0 0 20px", color: "#cbd5e1", lineHeight: "1.6" }}>
                  {(selectedSessionDetail.report.improvment_area || []).map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p style={{ color: "#94a3b8" }}>Interview has not been completed yet.</p>
            )}

            <button
              className="submit-btn-glow"
              onClick={() => setSelectedSessionDetail(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecruiterPage;
