import { ChevronRight, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const Breadcrumbs = ({ items }) => {
  const navigate = useNavigate();

  const handleClick = (path) => {
    if (path) {
      navigate(path);
    }
  };

  return (
    <nav className="breadcrumbs">
      <motion.button
        className="breadcrumb-item breadcrumb-home"
        onClick={() => handleClick('/')}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Home size={16} />
      </motion.button>

      {items.map((item, index) => (
        <div key={index} className="breadcrumb-segment">
          <ChevronRight size={16} className="breadcrumb-separator" />
          {item.path ? (
            <motion.button
              className="breadcrumb-item breadcrumb-link"
              onClick={() => handleClick(item.path)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {item.label}
            </motion.button>
          ) : (
            <span className="breadcrumb-item breadcrumb-current">
              {item.label}
            </span>
          )}
        </div>
      ))}
    </nav>
  );
};

export default Breadcrumbs;
