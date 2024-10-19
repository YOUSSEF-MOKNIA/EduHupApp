import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import Repositories from "./pages/Repositories";

// Example of a Protected Route Wrapper
const ProtectedRoute = ({ element }) => {
  const isAuthenticated = localStorage.getItem("token"); // Check if the user is authenticated

  return isAuthenticated ? element : <Login />; // Redirect to Login if not authenticated
};

function App() {
  return (
    <div className="bg-gray-100 min-h-screen"> {/* Add a wrapper div with a background color */}
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
          <Route path="/chat" element={<ProtectedRoute element={<Chat />} />} />
          <Route path="/repositories" element={<ProtectedRoute element={<Repositories />} />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
