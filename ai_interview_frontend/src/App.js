import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import RecruiterPage from "./pages/RecruiterPage";
import CandidatePage from "./pages/CandidatePage";
import InterviewPage from "./pages/InterviewPage";

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/recruiter" element={<RecruiterPage />} />
          <Route path="/candidate/:sessionId" element={<CandidatePage />} />
          <Route path="/practice" element={<InterviewPage />} />
          <Route path="*" element={<Navigate to="/recruiter" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
