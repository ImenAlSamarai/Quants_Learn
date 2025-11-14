import { motion } from 'framer-motion';
import { CheckCircle, ArrowRight, BookOpen, Clock, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import useAppStore from '../../store/useAppStore';

const StudyMode = ({ topic, categoryId }) => {
  const navigate = useNavigate();
  const { completedTopics, markTopicComplete, getRelatedTopics, topics, categories } = useAppStore();

  const isCompleted = completedTopics.includes(topic.id);
  const relatedTopics = getRelatedTopics(topic.id);

  // Get next topic in same category
  const categoryTopics = topics.filter((t) => t.category === categoryId);
  const currentIndex = categoryTopics.findIndex((t) => t.id === topic.id);
  const nextTopic = currentIndex < categoryTopics.length - 1 ? categoryTopics[currentIndex + 1] : null;

  const handleMarkComplete = () => {
    markTopicComplete(topic.id);
  };

  const handleNavigateToTopic = (topicId, catId) => {
    navigate(`/category/${catId}/topic/${topicId}`);
  };

  const getCategoryById = (catId) => {
    return categories.find((cat) => cat.id === catId);
  };

  const getDifficultyLabel = (difficulty) => {
    const labels = {
      1: 'Fundamental',
      2: 'Beginner',
      3: 'Intermediate',
      4: 'Advanced',
      5: 'Expert',
    };
    return labels[difficulty] || 'Unknown';
  };

  return (
    <motion.div
      className="study-mode"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Topic Header */}
      <div className="topic-header">
        <div className="topic-header-top">
          <div className="topic-icon-large">{topic.icon}</div>
          <div className="topic-meta-inline">
            <span className="topic-difficulty">
              <Star size={16} />
              {getDifficultyLabel(topic.difficulty)}
            </span>
            <span className="topic-reading-time">
              <Clock size={16} />
              ~5 min read
            </span>
          </div>
        </div>

        <h1 className="topic-title">{topic.name}</h1>

        {topic.description && (
          <p className="topic-description">{topic.description}</p>
        )}

        <div className="topic-actions">
          {!isCompleted ? (
            <motion.button
              className="btn-mark-complete"
              onClick={handleMarkComplete}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <CheckCircle size={18} />
              <span>Mark as Complete</span>
            </motion.button>
          ) : (
            <div className="completion-badge">
              <CheckCircle size={18} />
              <span>Completed</span>
            </div>
          )}
        </div>
      </div>

      {/* Prerequisites */}
      {topic.prerequisites && topic.prerequisites.length > 0 && (
        <div className="topic-prerequisites">
          <h3 className="section-title-small">
            <BookOpen size={18} />
            Prerequisites
          </h3>
          <div className="prerequisites-list">
            {topic.prerequisites.map((prereqId) => {
              const prereq = topics.find((t) => t.id === prereqId);
              if (!prereq) return null;
              const prereqCompleted = completedTopics.includes(prereqId);

              return (
                <motion.button
                  key={prereqId}
                  className={`prerequisite-item ${prereqCompleted ? 'completed' : ''}`}
                  onClick={() => handleNavigateToTopic(prereqId, prereq.category)}
                  whileHover={{ x: 4 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {prereqCompleted ? (
                    <CheckCircle size={16} className="prereq-icon-completed" />
                  ) : (
                    <BookOpen size={16} className="prereq-icon" />
                  )}
                  <span>{prereq.icon}</span>
                  <span>{prereq.name}</span>
                  {!prereqCompleted && <span className="prereq-badge">Required</span>}
                </motion.button>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="topic-content">
        <div className="content-section">
          <h2>Overview</h2>
          <p>
            {topic.content ||
              'This topic provides essential knowledge for understanding quantitative finance concepts. Explore the fundamentals and build a strong foundation for advanced topics.'}
          </p>
        </div>

        <div className="content-section">
          <h2>Key Concepts</h2>
          <ul className="key-concepts-list">
            <li>Understanding the core principles and definitions</li>
            <li>Practical applications in quantitative finance</li>
            <li>Common techniques and methodologies</li>
            <li>Real-world examples and case studies</li>
          </ul>
        </div>

        <div className="content-section">
          <h2>Practice</h2>
          <div className="practice-box">
            <p>💪 Interactive exercises and quizzes coming soon!</p>
          </div>
        </div>
      </div>

      {/* Related Topics */}
      {relatedTopics.length > 0 && (
        <div className="related-topics">
          <h3 className="section-title-small">
            <ArrowRight size={18} />
            Related Topics
          </h3>
          <div className="related-topics-grid">
            {relatedTopics.slice(0, 4).map((relatedTopic) => {
              const relatedCategory = getCategoryById(relatedTopic.category);
              return (
                <motion.button
                  key={relatedTopic.id}
                  className="related-topic-card"
                  onClick={() => handleNavigateToTopic(relatedTopic.id, relatedTopic.category)}
                  whileHover={{ y: -4, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="related-topic-icon">{relatedTopic.icon}</div>
                  <div className="related-topic-content">
                    <span className="related-topic-category">{relatedCategory?.name}</span>
                    <h4 className="related-topic-title">{relatedTopic.name}</h4>
                    <span className="related-topic-difficulty">
                      {'⭐'.repeat(relatedTopic.difficulty || 1)}
                    </span>
                  </div>
                  <ArrowRight size={16} className="related-topic-arrow" />
                </motion.button>
              );
            })}
          </div>
        </div>
      )}

      {/* Navigation Footer */}
      {nextTopic && (
        <div className="topic-footer">
          <motion.button
            className="btn-next-topic"
            onClick={() => handleNavigateToTopic(nextTopic.id, categoryId)}
            whileHover={{ x: 4 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="next-topic-content">
              <span className="next-topic-label">Next Topic</span>
              <span className="next-topic-title">
                {nextTopic.icon} {nextTopic.name}
              </span>
            </div>
            <ArrowRight size={20} />
          </motion.button>
        </div>
      )}
    </motion.div>
  );
};

export default StudyMode;
