import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import BottomNav from "./components/BottomNav";
import Home from "./pages/Home";
import ReportIssue from "./pages/ReportIssue";
import MyComplaints from "./pages/MyComplaints";
import CrewTasks from "./pages/CrewTasks";
import SupervisorDashboard from "./pages/SupervisorDashboard";
import ComplaintDetail from "./pages/ComplaintDetail";
import WorkforceEquipment from "./pages/WorkforceEquipment";
import PublicTransparencyFeed from "./pages/PublicTransparencyFeed";
import "./App.css";

function App() {
  const { user } = useAuth();

  return (
    <div className="app-shell">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/report" element={
            <ProtectedRoute allowedRoles={["citizen"]}><ReportIssue /></ProtectedRoute>
          } />
          <Route path="/my-complaints" element={
            <ProtectedRoute allowedRoles={["citizen"]}><MyComplaints /></ProtectedRoute>
          } />
          <Route path="/crew" element={
            <ProtectedRoute allowedRoles={["crew"]}><CrewTasks /></ProtectedRoute>
          } />
          <Route path="/dashboard" element={
            <ProtectedRoute allowedRoles={["admin"]}><SupervisorDashboard /></ProtectedRoute>
          } />
          <Route path="/workforce" element={
            <ProtectedRoute allowedRoles={["admin", "crew"]}><WorkforceEquipment /></ProtectedRoute>
          } />
          <Route path="/feed" element={
            <ProtectedRoute><PublicTransparencyFeed /></ProtectedRoute>
          } />
          <Route path="/complaint/:id" element={
            <ProtectedRoute><ComplaintDetail /></ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <BottomNav />
    </div>
  );
}

function ProtectedRoute({ children, allowedRoles }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/" replace />;
  return children;
}

export default App;
