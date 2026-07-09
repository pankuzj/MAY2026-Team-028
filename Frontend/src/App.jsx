import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import BottomNav from "./components/BottomNav";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Home from "./pages/Home";
import ReportComplaint from "./pages/ReportComplaint";
import MyComplaints from "./pages/MyComplaints";
import CrewTasks from "./pages/CrewTasks";
import SupervisorDashboard from "./pages/SupervisorDashboard";
import "./App.css";

function App() {
  return (
    <>
      <Navbar />
      <main className="app-main">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/report" element={
            <ProtectedRoute allowedRoles={["citizen"]}><ReportComplaint /></ProtectedRoute>
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
        </Routes>
      </main>
      <BottomNav />
    </>
  );
}

export default App;