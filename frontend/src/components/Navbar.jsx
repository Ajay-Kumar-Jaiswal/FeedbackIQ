import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi } from '../api/api';

export default function Navbar() {
  const navigate = useNavigate();
  const user = authApi.getCurrentUser();

  const handleLogout = () => {
    authApi.logout();
    navigate('/login');
  };

  return (
    <header style={styles.header}>
      <div style={styles.container}>
        <div style={styles.brandGroup}>
          <Link to="/" style={styles.logo}>
            Feedback<span style={{ color: '#4f46e5' }}>IQ</span>
          </Link>
          <span style={styles.badge}>MVP</span>
        </div>

        <nav style={styles.nav}>
          {user ? (
            <>
              <Link to="/" style={styles.navLink}>Feedback</Link>
              <span style={styles.userGreeting}>
                Hello, <strong>{user.name || user.email}</strong>
              </span>
              <button onClick={handleLogout} style={styles.logoutBtn}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" style={styles.navLink}>Login</Link>
              <Link to="/register" style={styles.registerBtn}>Register</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

const styles = {
  header: {
    background: '#ffffff',
    borderBottom: '1px solid #e2e8f0',
    position: 'sticky',
    top: 0,
    zIndex: 10,
  },
  container: {
    maxWidth: '1100px',
    margin: '0 auto',
    padding: '0.85rem 1.5rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  brandGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  logo: {
    fontSize: '1.25rem',
    fontWeight: '700',
    color: '#0f172a',
    textDecoration: 'none',
  },
  badge: {
    fontSize: '0.7rem',
    background: '#e0e7ff',
    color: '#4338ca',
    padding: '0.15rem 0.45rem',
    borderRadius: '4px',
    fontWeight: '600',
  },
  nav: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.2rem',
  },
  navLink: {
    color: '#475569',
    textDecoration: 'none',
    fontWeight: '500',
    fontSize: '0.95rem',
  },
  userGreeting: {
    fontSize: '0.9rem',
    color: '#64748b',
  },
  logoutBtn: {
    background: 'transparent',
    border: '1px solid #cbd5e1',
    color: '#475569',
    padding: '0.4rem 0.85rem',
    borderRadius: '6px',
    fontWeight: '500',
    fontSize: '0.85rem',
  },
  registerBtn: {
    background: '#4f46e5',
    color: '#ffffff',
    padding: '0.45rem 1rem',
    borderRadius: '6px',
    textDecoration: 'none',
    fontWeight: '500',
    fontSize: '0.9rem',
  }
};
