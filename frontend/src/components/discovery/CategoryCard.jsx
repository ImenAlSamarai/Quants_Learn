import { motion } from 'framer-motion';
import { ArrowRight, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import useAppStore from '../../store/useAppStore';

const CategoryCard = ({ category }) => {
  const navigate = useNavigate();
  const getCategoryProgress = useAppStore((state) => state.getCategoryProgress);
  const progress = getCategoryProgress(category.id);

  const handleClick = () => {
    navigate(`/category/${category.id}`);
  };

  return (
    <motion.div
      className="category-card"
      onClick={handleClick}
      whileHover={{ y: -8, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
    >
      <div className="category-card-header">
        <div className="category-icon-large">
          {category.icon}
        </div>
        {progress.completed > 0 && (
          <div className="category-badge">
            <CheckCircle size={16} />
            <span>{progress.completed}/{progress.total}</span>
          </div>
        )}
      </div>

      <div className="category-card-body">
        <h3 className="category-title">{category.name}</h3>
        <p className="category-description">{category.description}</p>

        <div className="category-meta">
          <div className="category-stats">
            <span className="stat-item">
              <span className="stat-label">Topics:</span>
              <span className="stat-value">{progress.total}</span>
            </span>
            <span className="stat-item">
              <span className="stat-label">Difficulty:</span>
              <span className="stat-value">{'⭐'.repeat(category.difficulty || 1)}</span>
            </span>
          </div>
        </div>

        {progress.total > 0 && (
          <div className="category-progress">
            <div className="progress-bar-container">
              <motion.div
                className="progress-bar-fill"
                initial={{ width: 0 }}
                animate={{ width: `${progress.percentage}%` }}
                transition={{ duration: 1, delay: 0.2, ease: 'easeOut' }}
              />
            </div>
            <span className="progress-label">{progress.percentage}% Complete</span>
          </div>
        )}
      </div>

      <div className="category-card-footer">
        <motion.button
          className="category-cta"
          whileHover={{ x: 4 }}
          transition={{ duration: 0.2 }}
        >
          <span>{progress.completed > 0 ? 'Continue Learning' : 'Start Learning'}</span>
          <ArrowRight size={18} />
        </motion.button>
      </div>
    </motion.div>
  );
};

export default CategoryCard;
