import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ChevronDown, ChevronRight, CheckCircle, Circle, Lock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import useAppStore from '../../store/useAppStore';

const Sidebar = ({ categoryId }) => {
  const navigate = useNavigate();
  const { topicId } = useParams();
  const { topics, completedTopics, sidebarCollapsed } = useAppStore();

  // Convert topicId from URL param (string) to number for comparison
  const activeTopicId = topicId ? parseInt(topicId, 10) || topicId : null;

  // Group topics by difficulty level
  const categoryTopics = topics.filter((topic) => topic.category === categoryId);

  const groupedTopics = categoryTopics.reduce((acc, topic) => {
    const level = topic.difficulty || 1;
    if (!acc[level]) {
      acc[level] = [];
    }
    acc[level].push(topic);
    return acc;
  }, {});

  const levels = Object.keys(groupedTopics).sort((a, b) => a - b);

  const [expandedLevels, setExpandedLevels] = useState(
    levels.reduce((acc, level) => ({ ...acc, [level]: true }), {})
  );

  const toggleLevel = (level) => {
    setExpandedLevels((prev) => ({
      ...prev,
      [level]: !prev[level],
    }));
  };

  const handleTopicClick = (topic) => {
    // Check if topic is locked (prerequisites not met)
    if (topic.prerequisites && topic.prerequisites.length > 0) {
      const allPrereqsMet = topic.prerequisites.every((prereqId) =>
        completedTopics.includes(prereqId)
      );
      if (!allPrereqsMet) {
        return; // Don't navigate if locked
      }
    }
    navigate(`/category/${categoryId}/topic/${topic.id}`);
  };

  const isTopicLocked = (topic) => {
    if (!topic.prerequisites || topic.prerequisites.length === 0) return false;
    return !topic.prerequisites.every((prereqId) => completedTopics.includes(prereqId));
  };

  const getLevelLabel = (level) => {
    const labels = {
      1: 'Fundamentals',
      2: 'Core Concepts',
      3: 'Intermediate',
      4: 'Advanced',
      5: 'Expert',
    };
    return labels[level] || `Level ${level}`;
  };

  if (sidebarCollapsed) {
    return null;
  }

  return (
    <motion.aside
      className="sidebar"
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -300, opacity: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
    >
      <div className="sidebar-content">
        <div className="sidebar-header">
          <h3>Topics</h3>
        </div>

        <nav className="sidebar-nav">
          {levels.map((level) => (
            <div key={level} className="topic-group">
              <button
                className="topic-group-header"
                onClick={() => toggleLevel(level)}
              >
                <span className="topic-group-icon">
                  {expandedLevels[level] ? (
                    <ChevronDown size={16} />
                  ) : (
                    <ChevronRight size={16} />
                  )}
                </span>
                <span className="topic-group-label">
                  {getLevelLabel(level)}
                </span>
                <span className="topic-group-count">
                  {groupedTopics[level].length}
                </span>
              </button>

              <AnimatePresence>
                {expandedLevels[level] && (
                  <motion.div
                    className="topic-list"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    {groupedTopics[level].map((topic) => {
                      const isCompleted = completedTopics.includes(topic.id);
                      const isLocked = isTopicLocked(topic);
                      const isActive = topic.id === activeTopicId;

                      return (
                        <motion.button
                          key={topic.id}
                          className={`topic-item ${isActive ? 'active' : ''} ${
                            isLocked ? 'locked' : ''
                          }`}
                          onClick={() => handleTopicClick(topic)}
                          disabled={isLocked}
                          whileHover={!isLocked ? { x: 4 } : {}}
                          whileTap={!isLocked ? { scale: 0.98 } : {}}
                        >
                          <span className="topic-item-icon">
                            {isCompleted ? (
                              <CheckCircle size={16} className="icon-completed" />
                            ) : isLocked ? (
                              <Lock size={16} className="icon-locked" />
                            ) : (
                              <Circle size={16} className="icon-default" />
                            )}
                          </span>
                          <span className="topic-item-emoji">{topic.icon}</span>
                          <span className="topic-item-label">{topic.name}</span>
                        </motion.button>
                      );
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </nav>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
