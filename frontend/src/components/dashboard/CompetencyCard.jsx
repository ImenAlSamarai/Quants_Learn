import React from 'react';
import '../../styles/dashboard.css';

const CompetencyCard = ({ competency }) => {
  const { category_display, completion_percent, level, topics_completed, topics_total } = competency;

  // Professional color scheme (Bloomberg-inspired)
  const getLevelColor = (level) => {
    switch (level) {
      case 'beginner':
        return '#64748b'; // Slate gray
      case 'intermediate':
        return '#3b82f6'; // Professional blue
      case 'advanced':
        return '#10b981'; // Professional green
      default:
        return '#94a3b8';
    }
  };

  const getLevelLabel = (level) => {
    switch (level) {
      case 'beginner':
        return 'Beginner';
      case 'intermediate':
        return 'Intermediate';
      case 'advanced':
        return 'Advanced';
      default:
        return 'Not Started';
    }
  };

  return (
    <div className="competency-card">
      <div className="competency-card-header">
        <h3 className="competency-card-title">{category_display}</h3>
        <span
          className="competency-level-badge"
          style={{ backgroundColor: getLevelColor(level) }}
        >
          {getLevelLabel(level)}
        </span>
      </div>

      <div className="competency-progress">
        <div className="competency-progress-bar-container">
          <div
            className="competency-progress-bar-fill"
            style={{
              width: `${completion_percent}%`,
              backgroundColor: getLevelColor(level),
            }}
          />
        </div>
        <div className="competency-progress-text">
          <span className="competency-percent">{completion_percent}%</span>
          <span className="competency-topics">
            {topics_completed} / {topics_total} topics
          </span>
        </div>
      </div>
    </div>
  );
};

export default CompetencyCard;
