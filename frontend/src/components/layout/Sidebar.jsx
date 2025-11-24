import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ChevronDown, ChevronRight, CheckCircle, Circle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import useAppStore from '../../store/useAppStore';

const Sidebar = ({ categoryId }) => {
  const navigate = useNavigate();
  const { topicId } = useParams();
  const { topics, isTopicCompleted, sidebarCollapsed } = useAppStore();

  // Convert topicId from URL param (string) to number for comparison
  const activeTopicId = topicId ? parseInt(topicId, 10) || topicId : null;

  // Group topics by learning path (or fallback to difficulty if not set)
  const categoryTopics = topics.filter((topic) => topic.category === categoryId);

  // Check if topics have learning_path metadata
  const hasLearningPaths = categoryTopics.some(
    (topic) => topic.extra_metadata?.learning_path
  );

  const groupedTopics = categoryTopics.reduce((acc, topic) => {
    // Use learning_path if available, otherwise fall back to difficulty
    const groupKey = hasLearningPaths
      ? topic.extra_metadata?.learning_path || 'ungrouped'
      : `diff_${topic.difficulty || 1}`;

    if (!acc[groupKey]) {
      acc[groupKey] = {
        topics: [],
        sequence: topic.extra_metadata?.sequence_order || 999,
        name: groupKey,
      };
    }
    acc[groupKey].topics.push(topic);
    return acc;
  }, {});

  // Sort groups and topics within each group
  const sortedGroups = Object.entries(groupedTopics)
    .sort(([keyA, groupA], [keyB, groupB]) => {
      if (hasLearningPaths) {
        // Sort by path order (foundational first)
        const orderMap = {
          'classical_ml_linear': 1,
          'classical_ml_classification': 2,
          'classical_ml_trees': 3,
          'classical_ml_unsupervised': 4,
          'classical_ml_assessment': 5,
          'dl_foundations': 6,
          'dl_training': 7,
          'dl_cnns': 8,
          'dl_transformers': 9,
        };
        return (orderMap[keyA] || 999) - (orderMap[keyB] || 999);
      } else {
        // Sort by difficulty
        return keyA.localeCompare(keyB);
      }
    });

  // Sort topics within each group by sequence_order
  sortedGroups.forEach(([_, group]) => {
    group.topics.sort((a, b) => {
      const seqA = a.extra_metadata?.sequence_order || 999;
      const seqB = b.extra_metadata?.sequence_order || 999;
      return seqA - seqB;
    });
  });

  const levels = sortedGroups.map(([key]) => key);

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
    navigate(`/category/${categoryId}/topic/${topic.id}`);
  };

  const getLevelLabel = (level) => {
    if (!hasLearningPaths) {
      // Fallback: difficulty-based labels
      const diffLevel = level.replace('diff_', '');
      const labels = {
        1: 'Fundamentals',
        2: 'Core Concepts',
        3: 'Intermediate',
        4: 'Advanced',
        5: 'Expert',
      };
      return labels[diffLevel] || `Level ${diffLevel}`;
    }

    // Learning path labels
    const pathLabels = {
      'classical_ml_linear': '📈 Linear Models',
      'classical_ml_classification': '🎯 Classification',
      'classical_ml_trees': '🌳 Tree Methods',
      'classical_ml_unsupervised': '🔍 Unsupervised Learning',
      'classical_ml_assessment': '📊 Model Assessment',
      'dl_foundations': '⭐ DL Foundations',
      'dl_training': '🎓 DL Training',
      'dl_cnns': '🖼️ CNNs',
      'dl_transformers': '💬 Transformers',
      'ungrouped': 'Other Topics',
    };
    return pathLabels[level] || level.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
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
          {levels.map((level) => {
            const group = groupedTopics[level];
            const topicsInGroup = group.topics;

            return (
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
                    {topicsInGroup.length}
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
                      {topicsInGroup.map((topic) => {
                        const isCompleted = isTopicCompleted(topic.id);
                        const isActive = topic.id === activeTopicId;
                        // Check if prerequisites are met (for greying out)
                        const prereqIds = topic.extra_metadata?.prerequisites_ids || [];
                        const hasUnmetPrereqs = prereqIds.some(
                          (prereqId) => !isTopicCompleted(prereqId)
                        );
                        const shouldGrey = hasUnmetPrereqs && !isCompleted && !isActive;

                        return (
                          <motion.button
                            key={topic.id}
                            className={`topic-item ${isActive ? 'active' : ''} ${shouldGrey ? 'greyed' : ''}`}
                            onClick={() => handleTopicClick(topic)}
                            whileHover={{ x: 4 }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <span className="topic-item-icon">
                              {isCompleted ? (
                                <CheckCircle size={16} className="icon-completed" />
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
            );
          })}
        </nav>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
