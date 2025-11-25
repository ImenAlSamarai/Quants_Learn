import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain } from 'lucide-react';
import CategoryCard from '../components/discovery/CategoryCard';
import ProgressStats from '../components/discovery/ProgressStats';
import CompetencyCard from '../components/dashboard/CompetencyCard';
import useAppStore from '../store/useAppStore';
import { getUserDashboard } from '../services/api';

const LandingPage = () => {
  const categories = useAppStore((state) => state.categories);
  const [competencies, setCompetencies] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [recommendedTopics, setRecommendedTopics] = useState([]);

  useEffect(() => {
    // Fetch dashboard data for competencies and activity
    const fetchDashboardData = async () => {
      try {
        const data = await getUserDashboard('demo_user');
        setCompetencies(data.competencies || []);
        setRecentActivity(data.recent_activity || []);
        setRecommendedTopics(data.recommended_topics || []);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };
    fetchDashboardData();
  }, []);

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <motion.section
        className="hero-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="hero-content">
          <motion.div
            className="hero-icon"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          >
            <Brain size={48} strokeWidth={1.5} />
          </motion.div>
          <h1 className="hero-title">
            Master Quantitative Finance
          </h1>
          <p className="hero-subtitle">
            Explore interconnected topics, build deep understanding, and advance your quant skills
            through interactive learning paths
          </p>
        </div>
      </motion.section>

      {/* Progress Stats */}
      <section className="stats-section">
        <ProgressStats />
      </section>

      {/* Competencies Grid */}
      {competencies.length > 0 && (
        <motion.section
          className="competencies-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="section-header">
            <h2 className="section-title">Your Competencies</h2>
            <p className="section-subtitle">
              Track your mastery across different categories
            </p>
          </div>
          <div className="competencies-grid">
            {competencies.map((comp) => (
              <CompetencyCard key={comp.category} competency={comp} />
            ))}
          </div>
        </motion.section>
      )}

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
