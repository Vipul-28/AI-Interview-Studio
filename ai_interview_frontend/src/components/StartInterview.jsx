import { useState } from "react";
import "../assets/css/StartInterview.css";
import { generateQuestionsAPI, startInterviewAPI } from "../services/interview";
import { ROLE_PRESETS } from "../util/rolePresets";

const ALLOWED_FILE = ["application/pdf"];
const MAX_FILE_SIZE = 5 * 1024 * 1024;

const StartInterview = ({ onClick }) => {
  const [selectedRoleId, setSelectedRoleId] = useState(ROLE_PRESETS[0].id);
  const [jobTitle, setJobTitle] = useState(ROLE_PRESETS[0].title);
  const [jobDescription, setJobDescription] = useState(ROLE_PRESETS[0].description);
  const [githubUrl, setGithubUrl] = useState("");
  const [resume, setResume] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

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

  const handleFileUpload = (e) => {
    try {
      const file = e.target.files[0];
      if (!file) return;

      if (!ALLOWED_FILE.includes(file.type)) {
        setError("Only PDF resume files are supported.");
        return;
      }

      if (file.size > MAX_FILE_SIZE) {
        setError("Resume file size must be under 5MB.");
        return;
      }

      setError("");
      setResume(file);
    } catch (error) {
      console.error("Error: ", error);
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();

    if (!jobTitle || !jobDescription || !resume) {
      setError("Job Title, Job Description, and Resume PDF are required.");
      return;
    }

    // Check microphone permission before proceeding
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Your browser does not support audio recording. Please use Chrome or Edge.");
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
    } catch (micErr) {
      console.error("Microphone permission denied:", micErr);
      setError(
        "🎤 Microphone access is required for the interview. Please click the lock/settings icon in your browser address bar, allow microphone access, and try again."
      );
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("job_title", jobTitle);
      formData.append("job_description", jobDescription);
      if (githubUrl && githubUrl.trim()) {
        formData.append("github_url", githubUrl.trim());
      }
      formData.append("resume", resume);

      // Generate question endpoint
      const response = await generateQuestionsAPI(formData);

      // Start interview endpoint
      const data = await startInterviewAPI(response.session_id);

      onClick(data, response.session_id);
    } catch (error) {
      console.error("Error: ", error);
      setError("Failed to start interview. Please check your backend connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="start-interview-container">
      <form className="start-interview-form" onSubmit={handleFormSubmit}>
        <div className="start-interview-header">
          <span className="start-interview-badge">Candidate Practice Studio</span>
          <h1>AI Interview Studio</h1>
          <p className="start-interview-subtitle">
            Select a target role or customize criteria, then test your live voice responses
          </p>
        </div>

        {error && <p className="error-message">{error}</p>}

        {/* Role Presets */}
        <div className="role-preset-selector">
          <span className="section-label">Choose Role Track</span>
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
              <strong>Custom Role Mode:</strong> Test your voice responses for ANY custom position. Enter your custom role title and requirements below.
            </div>
          </div>
        )}

        <div className="form-group">
          <label>
            {selectedRoleId === "custom" ? "Custom Role Name" : "Job Title"}
          </label>
          <input
            type="text"
            placeholder={
              selectedRoleId === "custom"
                ? "e.g. Cybersecurity Analyst, Solutions Architect, QA Automation Lead"
                : "e.g. Senior Full Stack Engineer"
            }
            required
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
          />
        </div>

        {/* Dynamic GitHub Link for Software & Technical Roles */}
        {isSoftwareRole && (
          <div className="form-group github-field-box">
            <div className="github-label-row">
              <label style={{ margin: 0 }}>GitHub Repository or Profile URL (Optional)</label>
              <span className="github-tag">Code Context Powered</span>
            </div>
            <input
              type="url"
              placeholder="e.g. https://github.com/username or https://github.com/username/project-repo"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
            />
            <p className="field-hint">
              🔗 <strong>Smart Code Cross-Referencing:</strong> The AI inspects your GitHub repositories against the Job Description requirements. If a project in your repo matches the required skills, a targeted technical question will be asked directly about your actual code!
            </p>
          </div>
        )}

        <div className="form-group">
          <label>Job Description & Key Requirements</label>
          <textarea
            placeholder="Enter Job Description"
            required
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Resume (PDF)</label>
          <input
            type="file"
            accept=".pdf"
            required
            onChange={handleFileUpload}
          />
          {resume && (
            <span style={{ fontSize: "0.85rem", color: "#38bdf8", marginTop: "4px" }}>
              📄 Selected: {resume.name}
            </span>
          )}
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? "⚡ Analyzing Criteria & Generating Questions..." : "Enter Live Voice Studio"}
        </button>
      </form>
    </div>
  );
};

export default StartInterview;