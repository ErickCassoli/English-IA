import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import DashboardLayout from "./layouts/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import Practice from "./pages/Practice";
import Flashcards from "./pages/Flashcards";
import SettingsPage from "./pages/Settings";
import Quiz from "./pages/Quiz";
import Report from "./pages/Report";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/flashcards" element={<Flashcards />} />
          <Route path="/practice" element={<Practice />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/quiz/:sessionId" element={<Quiz />} />
          <Route path="/report/:sessionId" element={<Report />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
