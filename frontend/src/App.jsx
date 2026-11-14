import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import {
  HOME_ROUTE,
  JOBS_ROUTE,
  JOB_DETAILS_ROUTE,
  STATISTICS_ROUTE,
} from "./config/const";
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
          <Route
            path={HOME_ROUTE}
            element={<Navigate to={JOBS_ROUTE} replace />}
          />
          <Route path={JOBS_ROUTE} element={<JobsPage />} />
          <Route path={JOB_DETAILS_ROUTE} element={<JobPage />} />
          <Route path={STATISTICS_ROUTE} element={<StatisticsPage />} />
        </Routes>
        <Footer />
      </div>
    </BrowserRouter>
  );
};

export default App;
