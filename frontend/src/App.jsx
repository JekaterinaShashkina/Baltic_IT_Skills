import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import { Footer } from "./components/layout/Footer";
import { Header } from "./components/layout/Header";
import { JobsPage } from "./pages/JobsPage";
import { JobPage } from "./pages/JobPage";
import { StatisticsPage } from "./pages/StatisticsPage";

const App = () => {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Header />
        <Routes>
          <Route path="/" element={<Navigate to="/jobs" replace />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/jobs/:jobId" element={<JobPage />} />
          <Route path="/statistics" element={<StatisticsPage />} />
        </Routes>
        <Footer />
      </div>
    </BrowserRouter>
  );
};

export default App;
