import React from 'react';
import PropTypes from 'prop-types';
import './TopicHexagon.css';

/**
 * TopicHexagon - Hexagonal bubble for topic visualization
 *
 * Features:
 * - Color-coded by priority (RED/YELLOW/GREEN)
 * - 70% fill transparency
 * - Solid border for covered topics, dotted for uncovered
 * - Displays topic name in center
 */
const TopicHexagon = ({
  topic,
  priority = 'MEDIUM',
  covered = true,
  onClick,
  size = 120,
  className = ''
}) => {
  // Color scheme based on priority
  const getColorScheme = (priority) => {
    switch (priority) {
      case 'HIGH':
        return {
          border: '#EF4444',      // Red
          fill: 'rgba(239, 68, 68, 0.7)',  // Red with 70% opacity
          text: '#7F1D1D'         // Dark red for text
        };
      case 'MEDIUM':
        return {
          border: '#F59E0B',      // Orange/Yellow
          fill: 'rgba(245, 158, 11, 0.7)',  // Orange with 70% opacity
          text: '#78350F'         // Dark orange for text
        };
      case 'LOW':
        return {
          border: '#10B981',      // Green
          fill: 'rgba(16, 185, 129, 0.7)',  // Green with 70% opacity
          text: '#064E3B'         // Dark green for text
        };
      default:
        return {
          border: '#6B7280',      // Gray
          fill: 'rgba(107, 114, 128, 0.7)',  // Gray with 70% opacity
          text: '#1F2937'         // Dark gray for text
        };
    }
  };

  const colors = getColorScheme(priority);
  const borderStyle = covered ? 'solid' : 'dotted';

  // Hexagon path (pointy-top orientation)
  // Center at (size/2, size/2), radius = size/2.5
  const radius = size / 2.5;
  const centerX = size / 2;
  const centerY = size / 2;

  // Calculate hexagon points (pointy-top)
  const points = [];
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 3) * i - Math.PI / 6; // Start from top point
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    points.push(`${x},${y}`);
  }
  const pathData = `M ${points.join(' L ')} Z`;

  // Handle click
  const handleClick = () => {
    if (onClick) {
      onClick(topic);
    }
  };

  // Truncate long topic names
  const truncateName = (name, maxLength = 20) => {
    if (name.length <= maxLength) return name;
    return name.substring(0, maxLength - 3) + '...';
  };

  return (
    <div
      className={`topic-hexagon ${className}`}
      onClick={handleClick}
      style={{
        width: size,
        height: size,
        cursor: onClick ? 'pointer' : 'default'
      }}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="hexagon-svg"
      >
        {/* Hexagon fill */}
        <path
          d={pathData}
          fill={colors.fill}
          className="hexagon-fill"
        />

        {/* Hexagon border */}
        <path
          d={pathData}
          fill="none"
          stroke={colors.border}
          strokeWidth={covered ? 3 : 2}
          strokeDasharray={covered ? 'none' : '5,5'}
          className="hexagon-border"
        />

        {/* Topic name text */}
        <text
          x={centerX}
          y={centerY}
          textAnchor="middle"
          dominantBaseline="middle"
          fill={colors.text}
          fontSize={size > 100 ? 14 : 12}
          fontWeight="600"
          className="hexagon-text"
        >
          <tspan x={centerX} dy="0">{truncateName(topic, 18)}</tspan>
        </text>
      </svg>

      {/* Tooltip on hover */}
      <div className="hexagon-tooltip">
        <div className="tooltip-content">
          <div className="tooltip-name">{topic}</div>
          <div className="tooltip-meta">
            <span className={`priority-badge priority-${priority.toLowerCase()}`}>
              {priority}
            </span>
            <span className={`coverage-badge ${covered ? 'covered' : 'uncovered'}`}>
              {covered ? '✓ Covered' : '📚 Need resources'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

TopicHexagon.propTypes = {
  topic: PropTypes.string.isRequired,
  priority: PropTypes.oneOf(['HIGH', 'MEDIUM', 'LOW']),
  covered: PropTypes.bool,
  onClick: PropTypes.func,
  size: PropTypes.number,
  className: PropTypes.string
};

export default TopicHexagon;
