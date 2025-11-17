import { motion } from 'framer-motion';
import { ArrowRight, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import useAppStore from '../../store/useAppStore';

const RecommendedTopics = () => {
  const navigate = useNavigate();
  const { topics, completedTopics, categories } = useAppStore();

  // Get recommended topics (incomplete topics with completed prerequisites)
  let recommendedTopics = topics
    .filter((topic) => {
      if (completedTopics.includes(topic.id)) return false;
      if (!topic.prerequisites || topic.prerequisites.length === 0) return true;
      return topic.prerequisites.every((prereq) => completedTopics.includes(prereq));
    })
    .slice(0, 3);

  // Fallback for new users: show fundamental topics (difficulty 1) if no recommendations
  if (recommendedTopics.length === 0) {
    recommendedTopics = topics
      .filter((topic) => !completedTopics.includes(topic.id) && topic.difficulty === 1)
      .slice(0, 3);
  }

  // If still no topics, don't render the section
  if (recommendedTopics.length === 0) {
    return null;
  }

  const getCategoryName = (categoryId) => {
    const category = categories.find((cat) => cat.id === categoryId);
    return category?.name || 'Unknown';
  };

  const handleTopicClick = (topic) => {
    navigate(`/category/${topic.category}/topic/${topic.id}`);
  };

  // Check if showing fundamentals (for new users) or actual recommendations
  const isShowingFundamentals = completedTopics.length === 0;

  return (
    <div className="recommended-section">
      <div className="section-header">
        <div className="section-title">
          <Star size={24} className="section-icon" />
          <h2>{isShowingFundamentals ? 'Start Your Journey' : 'Recommended for You'}</h2>
        </div>
        <p className="section-subtitle">
          {isShowingFundamentals
            ? 'Begin with these fundamental topics to build a strong foundation'
            : 'Continue your learning journey with these topics'}
        </p>
      </div>

      <div className="recommended-grid">
        {recommendedTopics.map((topic, index) => (
          <motion.div
            key={topic.id}
            className="recommended-card"
            onClick={() => handleTopicClick(topic)}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1, duration: 0.3 }}
            whileHover={{ x: 4, scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
          >
            <div className="recommended-icon">{topic.icon}</div>
            <div className="recommended-content">
              <div className="recommended-category">
                {getCategoryName(topic.category)}
              </div>
              <h4 className="recommended-title">{topic.name}</h4>
              <p className="recommended-description">
                {topic.description?.substring(0, 100)}...
              </p>
              <div className="recommended-meta">
                <span className="difficulty-badge">
                  {'⭐'.repeat(topic.difficulty || 1)}
                </span>
                {topic.prerequisites && topic.prerequisites.length > 0 && (
                  <span className="prerequisites-badge">
                    Prerequisites met
                  </span>
                )}
              </div>
            </div>
            <motion.div
              className="recommended-arrow"
              whileHover={{ x: 4 }}
              transition={{ duration: 0.2 }}
            >
              <ArrowRight size={20} />
            </motion.div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default RecommendedTopics;
