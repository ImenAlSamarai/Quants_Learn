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
    navigate('/');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // TODO: Implement search functionality
      console.log('Searching for:', searchQuery);
    }
  };

  const handleLogout = () => {
    logout();
    setUser(null);
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
          <div className="brand-text">
            <h1>Quant Learning</h1>
            <p>Interactive Knowledge Platform</p>
          </div>
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
          {!isHome && (
            <motion.button
              onClick={handleLogoClick}
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
              <span className="user-greeting" style={{ marginRight: '1rem', color: '#C9A96E' }}>
                Hello, {user.name || user.user_id}
              </span>
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
              <motion.button
                onClick={() => navigate('/register')}
                className="header-action-btn header-action-btn-primary"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <UserPlus size={18} />
                <span className="action-label">Register</span>
              </motion.button>
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
