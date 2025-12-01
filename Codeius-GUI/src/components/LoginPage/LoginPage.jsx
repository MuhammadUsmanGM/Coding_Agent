import React from 'react';
import './LoginPage.css';

const LoginPage = () => {
  const handleGoogleLogin = () => {
    // Redirect to backend Google Auth endpoint
    window.location.href = 'http://localhost:5000/api/auth/google/login';
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <img src="/logo.png" alt="Codeius Logo" className="login-logo" />
        <h1 className="login-title">Welcome to Codeius</h1>
        <p className="login-subtitle">Sign in to sync your conversations and settings across all your devices.</p>

        <button className="google-btn" onClick={handleGoogleLogin}>
          <img 
            src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" 
            alt="Google" 
            className="google-icon" 
          />
          Continue with Google
        </button>

        <div className="divider">OR</div>

        <button className="guest-link">
          Continue as Guest (Local Only)
        </button>

        <div className="terms">
          By continuing, you agree to Codeius's<br />
          <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
