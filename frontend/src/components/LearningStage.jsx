import { useState } from 'react';

const LearningStage = ({ stage, stageNumber, isExpanded, onToggle }) => {
  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return '#ef4444'; // Red
      case 'medium':
        return '#f59e0b'; // Orange
      case 'low':
        return '#10b981'; // Green
      default:
        return '#6b7280'; // Gray
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return '🔥';
      case 'medium':
        return '⚡';
      case 'low':
        return '📌';
      default:
        return '•';
    }
  };

  return (
    <div className={`learning-stage ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="stage-header" onClick={onToggle}>
        <div className="stage-title-row">
          <div className="stage-number">Stage {stageNumber}</div>
          <h3 className="stage-name">{stage.stage_name}</h3>
          <button className="expand-btn">
            {isExpanded ? '▼' : '▶'}
          </button>
        </div>

        {stage.duration_weeks && (
          <div className="stage-duration">
            <span className="duration-icon">⏱️</span>
            <span>{stage.duration_weeks} weeks</span>
          </div>
        )}
      </div>

      {isExpanded && (
        <div className="stage-body">
          {stage.description && (
            <p className="stage-description">{stage.description}</p>
          )}

          {stage.topics && stage.topics.length > 0 && (
            <div className="stage-topics">
              <h4 className="topics-heading">Topics to Cover:</h4>
              <div className="topics-list">
                {stage.topics.map((topic, index) => (
                  <div key={index} className="stage-topic-card">
                    <div className="topic-main">
                      <div className="topic-title-row">
                        {topic.priority && (
                          <span
                            className="priority-badge"
                            style={{ backgroundColor: getPriorityColor(topic.priority) }}
                          >
                            {getPriorityIcon(topic.priority)} {topic.priority}
                          </span>
                        )}
                        <span className="topic-title">{topic.title}</span>
                      </div>

                      {topic.why && (
                        <p className="topic-why">
                          <strong>Why:</strong> {topic.why}
                        </p>
                      )}
                    </div>

                    {topic.node_id && (
                      <button
                        onClick={() => window.location.href = `/node/${topic.node_id}`}
                        className="start-learning-btn"
                      >
                        Start Learning →
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {stage.prerequisites && stage.prerequisites.length > 0 && (
            <div className="stage-prerequisites">
              <h4 className="prerequisites-heading">📋 Prerequisites:</h4>
              <ul>
                {stage.prerequisites.map((prereq, index) => (
                  <li key={index}>{prereq}</li>
                ))}
              </ul>
            </div>
          )}

          {stage.interview_tips && stage.interview_tips.length > 0 && (
            <div className="stage-interview-tips">
              <h4 className="tips-heading">💼 Interview Tips:</h4>
              <ul>
                {stage.interview_tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LearningStage;
