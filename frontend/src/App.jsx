import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import HomePage from './components/HomePage';
import OpportunitiesList from './components/OpportunitiesList';
import EventsList from './components/EventsList';
import Login from './components/Login';
import Register from './components/Register';
import UserProfile from './components/UserProfile';
import AdminPanel from './components/AdminPanel';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ErrorPage from './components/ErrorPage';
import './App.css';

// Active link component with animated underline
const ActiveLink = ({ to, children }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <NavLink 
      to={to} 
      className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
    >
      {children}
      <motion.div 
        className="link-underline"
        initial={{ width: "0%" }}
        animate={{ width: isActive ? "100%" : "0%" }}
        transition={{ duration: 0.3 }}
      />
    </NavLink>
  );
};

// Loading screen component
const LoadingScreen = ({ isLoading }) => {
  return (
    <AnimatePresence>
      {isLoading && (
        <motion.div 
          className="loading-screen"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div className="loading-content">
            <motion.div 
              className="loading-logo"
              animate={{ 
                scale: [1, 1.1, 1],
                rotate: [0, 5, -5, 0]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatType: "loop"
              }}
            >
              🔬
            </motion.div>
            <motion.div 
              className="loading-bar"
              initial={{ width: "0%" }}
              animate={{ width: "100%" }}
              transition={{ duration: 1.5 }}
            />
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              Loading amazing research opportunities...
            </motion.p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// Navigation with auth state
const Navigation = () => {
  const { isAuthenticated, isAdmin, isUser, userData, logout } = useAuth();
  const location = useLocation();
  
  return (
    <div className="navbar">
      <div className="navbar-content">
        <div className="logo">
          <ActiveLink to="/">ResearchHub</ActiveLink>
        </div>
        <div className="nav-links">
          <ActiveLink to="/">Home</ActiveLink>
          <ActiveLink to="/events">Events</ActiveLink>
          <ActiveLink to="/opportunities">Opportunities</ActiveLink>
        </div>
        <div className="auth-links">
          {isAuthenticated ? (
            <>
              {isUser && (
                <NavLink 
                  to="/profile" 
                  className="auth-button profile"
                >
                  {userData?.username || 'Profile'}
                </NavLink>
              )}
              {isAdmin && (
                <NavLink 
                  to="/admin" 
                  className="auth-button admin"
                >
                  Admin Panel
                </NavLink>
              )}
              <button 
                onClick={logout} 
                className="auth-button logout"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink 
                to="/login" 
                className="auth-button login"
              >
                Login
              </NavLink>
              <NavLink 
                to="/register" 
                className="auth-button register"
              >
                Sign Up
              </NavLink>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading time
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);
    
    return () => clearTimeout(timer);
  }, []);

  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <LoadingScreen isLoading={isLoading} />
          
          {!isLoading && (
            <>
              <Navigation />
              
              <main>
                <AnimatePresence mode="wait">
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/events" element={<EventsList />} />
                    <Route path="/opportunities" element={<OpportunitiesList />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/profile" element={
                      <ProtectedRoute>
                        <UserProfile />
                      </ProtectedRoute>
                    } />
                    <Route path="/admin" element={
                      <ProtectedRoute adminOnly={true}>
                        <AdminPanel />
                      </ProtectedRoute>
                    } />
                    <Route path="*" element={<ErrorPage />} />
                  </Routes>
                </AnimatePresence>
              </main>
            </>
          )}
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;