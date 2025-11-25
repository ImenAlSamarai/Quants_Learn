import React, { useState, useEffect } from 'react';
import { getUserDashboard } from '../../services/api';
import ProfileSummary from './ProfileSummary';
import CompetencyCard from './CompetencyCard';
import '../../styles/dashboard.css';

const ProgressDashboard = ({ userId = 'demo_user' }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, [userId]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await getUserDashboard(userId);
      setDashboardData(data);
      setError(null);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading your progress dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <p>{error}</p>
        <button onClick={loadDashboardData} className="btn-retry">
          Retry
        </button>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const { profile, interview_readiness, competencies, recent_activity, recommended_topics, study_streak_days } = dashboardData;

  return (
    <div className="progress-dashboard">
      {/* Profile Summary Section */}
      <section className="dashboard-section">
        <ProfileSummary
          profile={profile}
          interviewReadiness={interview_readiness}
        />
      </section>

      {/* Competencies Grid */}
      <section className="dashboard-section">
        <h2 className="section-title">Competencies</h2>
        <div className="competencies-grid">
          {competencies && competencies.length > 0 ? (
            competencies.map((comp) => (
              <CompetencyCard key={comp.category} competency={comp} />
            ))
          ) : (
            <p className="no-data">No competency data available. Start learning to build your skills!</p>
          )}
        </div>
      </section>

      {/* Activity & Recommendations */}
      <div className="dashboard-row">
        {/* Recent Activity */}
        <section className="dashboard-section dashboard-half">
          <h2 className="section-title">Recent Activity</h2>
          {study_streak_days > 0 && (
            <div className="study-streak">
              <span className="streak-icon">🔥</span>
              <span className="streak-text">{study_streak_days} day{study_streak_days !== 1 ? 's' : ''} streak</span>
            </div>
          )}
          <div className="activity-list">
            {recent_activity && recent_activity.length > 0 ? (
              recent_activity.map((activity) => (
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
              <p className="no-data">No recent activity. Start studying to see your progress here!</p>
            )}
          </div>
        </section>

        {/* Recommended Topics */}
        <section className="dashboard-section dashboard-half">
          <h2 className="section-title">Recommended Next</h2>
          <div className="recommendations-list">
            {recommended_topics && recommended_topics.length > 0 ? (
              recommended_topics.map((topic) => (
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
        </section>
      </div>
    </div>
  );
};

export default ProgressDashboard;
