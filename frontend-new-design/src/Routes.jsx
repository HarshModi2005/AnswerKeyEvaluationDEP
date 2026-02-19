import React from "react";
import { BrowserRouter, Routes as RouterRoutes, Route } from "react-router-dom";
import ScrollToTop from "./components/ScrollToTop";
import ErrorBoundary from "./components/ErrorBoundary";

// Page imports
import LoginRegister from "./pages/login-register";
import DashboardOverview from "./pages/dashboard-overview";
import KanbanBoard from "./pages/kanban-board";
import SprintPlanning from "./pages/sprint-planning";
import TaskDetail from "./pages/task-detail";
import AnalyticsDashboard from "./pages/analytics-dashboard";
import TeamManagement from "./pages/team-management";
import FacultyDashboard from "./pages/faculty-dashboard";
import CourseDetail from "./pages/course-detail";

const Routes = () => {
    return (
        <BrowserRouter>
            <ErrorBoundary>
                <ScrollToTop />
                <RouterRoutes>
                    <Route path="/login-register" element={<LoginRegister />} />
                    <Route path="/dashboard-overview" element={<DashboardOverview />} />
                    <Route path="/kanban-board" element={<KanbanBoard />} />
                    <Route path="/sprint-planning" element={<SprintPlanning />} />
                    <Route path="/task-detail" element={<TaskDetail />} />
                    <Route path="/analytics-dashboard" element={<AnalyticsDashboard />} />
                    <Route path="/team-management" element={<TeamManagement />} />
                    <Route path="/faculty-dashboard" element={<FacultyDashboard />} />
                    <Route path="/course/:courseId" element={<CourseDetail />} />
                    <Route path="/" element={<LoginRegister />} />
                </RouterRoutes>
            </ErrorBoundary>
        </BrowserRouter>
    );
};

export default Routes;