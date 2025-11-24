import { motion } from 'framer-motion';
import { TrendingUp, Target, Award, Clock } from 'lucide-react';
import useAppStore from '../../store/useAppStore';

const ProgressStats = () => {
  const { isTopicCompleted, topics, learningLevel } = useAppStore();

  const totalTopics = topics.length;
  const completed = topics.filter((topic) => isTopicCompleted(topic.id)).length;
  const percentage = totalTopics > 0 ? Math.round((completed / totalTopics) * 100) : 0;

  // Get level label based on learningLevel
  const getLevelLabel = () => {
    const levels = {
      1: '🌱 Beginner',
      2: '📚 Foundation',
      3: '🎓 Graduate',
      4: '🔬 Researcher',
      5: '⭐ Expert',
    };
    return levels[learningLevel] || '🌱 Beginner';
  };

  const stats = [
    {
      icon: <Target size={20} />,
      label: 'Topics Completed',
      value: `${completed}/${totalTopics}`,
      color: 'sage',
    },
    {
      icon: <TrendingUp size={20} />,
      label: 'Overall Progress',
      value: `${percentage}%`,
      color: 'ocean',
    },
    {
      icon: <Award size={20} />,
      label: 'Learning Level',
      value: getLevelLabel(),
      color: 'gold',
    },
    {
      icon: <Clock size={20} />,
      label: 'Current Streak',
      value: '0 days',
      color: 'terracotta',
    },
  ];

  return (
    <div className="progress-stats-container">
      <div className="stats-grid">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            className={`stat-card stat-card-${stat.color}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.3 }}
          >
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-content">
              <div className="stat-value">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default ProgressStats;
