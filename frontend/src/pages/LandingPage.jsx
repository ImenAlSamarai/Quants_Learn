/**
 * ⚠️ DEPRECATED - DO NOT USE FOR NEW FEATURES
 *
 * This component is from the old explore-based navigation system.
 * It has been replaced by the job-based personalization system.
 *
 * Current main page: frontend/src/pages/Home.jsx (route: /)
 * This file (route: /explore) is kept for backward compatibility only.
 *
 * Deprecated: 2025-11-28 (Phase 3 - Job-based personalization)
 * TODO: Remove this file in refactoring Phase 5
 *
 * Last active use: Before Phase 3 completion
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import CategoryCard from '../components/discovery/CategoryCard';
import useAppStore from '../store/useAppStore';
import { getUserDashboard } from '../services/api';

const LandingPage = () => {
  const categories = useAppStore((state) => state.categories);
  const learningLevel = useAppStore((state) => state.learningLevel);
  const [recentActivity, setRecentActivity] = useState([]);
  const [recommendedTopics, setRecommendedTopics] = useState([]);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    // Fetch dashboard data for activity and recommendations
    const fetchDashboardData = async () => {
      try {
        const data = await getUserDashboard('demo_user');
        setRecentActivity(data.recent_activity || []);
        setRecommendedTopics(data.recommended_topics || []);
        setUserName(data.profile?.name || 'demo_user');
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };
    fetchDashboardData();
  }, []);

  // Get level label based on learningLevel
  const getLevelLabel = () => {
    const levels = {
      1: '🌱 Beginner',
      2: '📚 Foundation',
      3: '🎓 Graduate',
      4: '🔬 Researcher',
      5: '⭐ Expert',
    };
    return levels[learningLevel] || '🎓 Graduate';
  };

  return (
    <div className="landing-page">
      {/* Page Title */}
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h1 className="page-title">Master Quantitative Finance</h1>
        <p className="page-subtitle">Your personalized learning journey</p>
      </motion.div>

      {/* User Info - Top Right */}
      <motion.div
        className="user-info-bar"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <div className="user-info-content">
          <span className="user-name">
            {userName || 'Loading...'}
            <span className="greeting"> Hello World!</span>
          </span>
          <span className="user-level">{getLevelLabel()}</span>
        </div>
      </motion.div>

      {/* Categories Grid */}
      <section className="categories-section">
        <div className="section-header">
          <h2 className="section-title">Learning Paths</h2>
          <p className="section-subtitle">
            Choose a category to begin your journey
          </p>
        </div>

        <div className="categories-grid">
          {categories.map((category, index) => (
            <CategoryCard key={category.id} category={category} />
          ))}
        </div>
      </section>

      {/* Activity & Recommendations */}
      <motion.section
        className="activity-recommendations-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className="dashboard-row">
          {/* Recent Activity */}
          <div className="dashboard-section dashboard-half">
            <h2 className="section-title">Recent Activity</h2>
            <div className="activity-list">
              {recentActivity.length > 0 ? (
                recentActivity.map((activity) => (
                  <div key={activity.node_id} className="activity-item">
                    <div className="activity-info">
                      <span className="activity-title">{activity.title}</span>
                      <span className="activity-category">{activity.category}</span>
                    </div>
                    <div className="activity-progress">
                      <div className="progress-mini-bar">
                        <div
                          className="progress-mini-fill"
                          style={{ width: `${activity.completion}%` }}
                        />
                      </div>
                      <span className="progress-mini-text">{activity.completion}%</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="no-data">Start studying to see your recent progress here!</p>
              )}
            </div>
          </div>

          {/* Recommended Topics */}
          <div className="dashboard-section dashboard-half">
            <h2 className="section-title">Recommended Next</h2>
            <div className="recommendations-list">
              {recommendedTopics.length > 0 ? (
                recommendedTopics.map((topic) => (
                  <div key={topic.node_id} className="recommendation-item">
                    <div className="recommendation-info">
                      <span className="recommendation-title">{topic.title}</span>
                      <span className="recommendation-category">{topic.category}</span>
                    </div>
                    {topic.estimated_time && (
                      <span className="recommendation-time">
                        ⏱️ {topic.estimated_time} min
                      </span>
                    )}
                  </div>
                ))
              ) : (
                <p className="no-data">Complete more topics to get personalized recommendations!</p>
              )}
            </div>
          </div>
        </div>
      </motion.section>

      {/* Quick Tips */}
      <motion.section
        className="tips-section"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <div className="tips-content">
          <h3 className="tips-title">💡 Learning Tips</h3>
          <ul className="tips-list">
            <li>Start with fundamentals before advancing to complex topics</li>
            <li>Complete prerequisite topics to unlock new content</li>
            <li>Switch between Study and Explore modes to visualize connections</li>
            <li>Track your progress and maintain consistency</li>
          </ul>
        </div>
      </motion.section>
    </div>
  );
};

export default LandingPage;
