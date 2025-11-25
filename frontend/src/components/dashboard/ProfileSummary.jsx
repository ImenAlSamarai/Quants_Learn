import React from 'react';
import '../../styles/dashboard.css';

const ProfileSummary = ({ profile, interviewReadiness }) => {
  const { name, email, education_level, job_role, completion_percent } = profile;

  // Format education level for display
  const formatEducationLevel = (level) => {
    if (!level) return 'Not specified';
    return level.charAt(0).toUpperCase() + level.slice(1).replace('_', ' ');
  };

  // Color for profile completion
  const getCompletionColor = (percent) => {
    if (percent >= 75) return '#10b981'; // Green
    if (percent >= 50) return '#3b82f6'; // Blue
    if (percent >= 25) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  // Color for interview readiness
  const getReadinessColor = (score) => {
    if (score >= 75) return '#10b981';
    if (score >= 50) return '#3b82f6';
    if (score >= 25) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="profile-summary">
      <div className="profile-summary-header">
        <div className="profile-avatar">
          {name ? name.charAt(0).toUpperCase() : '?'}
        </div>
        <div className="profile-info">
          <h2 className="profile-name">{name || 'Anonymous'}</h2>
          <p className="profile-email">{email || 'No email provided'}</p>
          <div className="profile-details">
            <span className="profile-education">{formatEducationLevel(education_level)}</span>
            {job_role && (
              <>
                <span className="profile-separator">•</span>
                <span className="profile-role">{job_role}</span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="profile-metrics">
        <div className="profile-metric">
          <div className="profile-metric-label">Profile Completion</div>
          <div className="profile-metric-value-container">
            <div className="circular-progress">
              <svg viewBox="0 0 36 36" className="circular-chart">
                <path
                  className="circle-bg"
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="circle"
                  strokeDasharray={`${completion_percent}, 100`}
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                  style={{ stroke: getCompletionColor(completion_percent) }}
                />
                <text x="18" y="20.35" className="percentage">
                  {completion_percent}%
                </text>
              </svg>
            </div>
          </div>
        </div>

        <div className="profile-metric">
          <div className="profile-metric-label">Interview Readiness</div>
          <div className="profile-metric-value-container">
            <div className="circular-progress">
              <svg viewBox="0 0 36 36" className="circular-chart">
                <path
                  className="circle-bg"
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="circle"
                  strokeDasharray={`${interviewReadiness}, 100`}
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                  style={{ stroke: getReadinessColor(interviewReadiness) }}
                />
                <text x="18" y="20.35" className="percentage">
                  {interviewReadiness}
                </text>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileSummary;
