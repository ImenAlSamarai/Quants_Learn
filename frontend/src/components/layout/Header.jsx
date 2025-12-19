import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Brain, Search, Settings, BarChart3, Home, LogIn, LogOut, UserPlus } from 'lucide-react';
import { motion } from 'framer-motion';
import { isAuthenticated, getUser, logout } from '../../services/auth';

const Header = ({ onShowAdmin }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');
  const [user, setUser] = useState(null);
  const isHome = location.pathname === '/';

  useEffect(() => {
    if (isAuthenticated()) {
      setUser(getUser());
    }
  }, [location]);

  const handleLogoClick = () => {
    // Navigate to dashboard if authenticated, otherwise home
    if (user || isAuthenticated()) {
      navigate('/dashboard');
    } else {
      navigate('/');
    }
  };

  const handleHomeClick = () => {
    // Same logic for Home button - always go to dashboard if user exists
    if (user || isAuthenticated()) {
      navigate('/dashboard');
    } else {
      navigate('/');
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      alert('🔍 Search feature coming soon! You\'ll be able to search across all topics, sections, and learning materials.');
      console.log('Searching for:', searchQuery);
    }
  };

  const handleLogout = async () => {
    // Clear user state FIRST
    setUser(null);

    // AWAIT logout to ensure localStorage is cleared BEFORE navigation
    await logout();

    // Show success notification
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = '✓ Your progress has been saved. See you next time!';
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease-in';
      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification);
        }
      }, 300);
    }, 3000);

    // Navigate AFTER logout completes
    navigate('/');
  };

  return (
    <motion.header
      className="app-header-new"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      <div className="header-container">
        {/* Brand */}
        <motion.div
          className="header-brand-new"
          onClick={handleLogoClick}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Brain size={32} color="#C9A96E" strokeWidth={2} />
          {!isHome && (
            <div className="brand-text">
              <h1>The Ethical Hiring Platform</h1>
            </div>
          )}
        </motion.div>

        {/* Search Bar - Only show when not on home */}
        {!isHome && (
          <motion.form
            className="header-search"
            onSubmit={handleSearch}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder="Search topics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </motion.form>
        )}

        {/* Actions */}
        <div className="header-actions">
          {user && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              padding: '0.5rem 1rem',
              background: 'rgba(201, 169, 110, 0.1)',
              borderRadius: '8px',
              marginRight: '1rem',
              border: '1px solid rgba(201, 169, 110, 0.2)'
            }}>
              <span style={{
                fontSize: '0.875rem',
                fontWeight: '600',
                color: '#C9A96E'
              }}>
                Hello, {user.name || user.user_id}
              </span>
            </div>
          )}

          {!isHome && (
            <motion.button
              onClick={handleHomeClick}
              className="header-action-btn"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Home size={18} />
              <span className="action-label">Home</span>
            </motion.button>
          )}

          {user ? (
            <>
              <motion.button
                onClick={handleLogout}
                className="header-action-btn"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <LogOut size={18} />
                <span className="action-label">Logout</span>
              </motion.button>
            </>
          ) : (
            <>
              <motion.button
                onClick={() => navigate('/login')}
                className="header-action-btn"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <LogIn size={18} />
                <span className="action-label">Login</span>
              </motion.button>
              {!isHome && (
                <motion.button
                  onClick={() => navigate('/register')}
                  className="header-action-btn header-action-btn-primary"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <UserPlus size={18} />
                  <span className="action-label">Register</span>
                </motion.button>
              )}
            </>
          )}

          <motion.button
            onClick={onShowAdmin}
            className="header-action-btn"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <BarChart3 size={18} />
            <span className="action-label">Admin</span>
          </motion.button>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
