import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Target, Award, Clock } from 'lucide-react';
import useAppStore from '../../store/useAppStore';
import { getUserDashboard } from '../../services/api';

const ProgressStats = () => {
  const { isTopicCompleted, topics, learningLevel } = useAppStore();
  const [interviewReadiness, setInterviewReadiness] = useState(0);
  const [studyStreak, setStudyStreak] = useState(0);

  useEffect(() => {
    // Fetch dashboard data for interview readiness and streak
    const fetchDashboardData = async () => {
      try {
        const data = await getUserDashboard('demo_user');
        setInterviewReadiness(data.interview_readiness || 0);
        setStudyStreak(data.study_streak_days || 0);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };
    fetchDashboardData();
  }, []);

  const totalTopics = topics.length;
  const completed = topics.filter((topic) => isTopicCompleted(topic.id)).length;

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
      label: 'Interview Readiness',
      value: `${interviewReadiness}%`,
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
      label: 'Study Streak',
      value: `${studyStreak} day${studyStreak !== 1 ? 's' : ''}`,
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
