import React from 'react';
import PropTypes from 'prop-types';
import TopicHexagon from './TopicHexagon';
import './StagedTreeLayout.css';

/**
 * StagedTreeLayout - Clean horizontal tree visualization
 *
 * Simple left-to-right layout with proper arrow connections
 */
const StagedTreeLayout = ({
  stages = [],
  dependencies = [],
  onTopicClick,
  className = ''
}) => {
  const HEXAGON_SIZE = 140;
  const STAGE_SPACING = 300; // Horizontal spacing between stages
  const TOPIC_SPACING = 180; // Vertical spacing between topics

  // Calculate all topic positions
  const calculatePositions = () => {
    const positions = {};

    stages.forEach((stage, stageIndex) => {
      const topics = stage.topics || [];
      const x = stageIndex * STAGE_SPACING + 150; // Left margin

      topics.forEach((topic, topicIndex) => {
        const y = topicIndex * TOPIC_SPACING + 100; // Top margin
        positions[topic.name] = {
          x,
          y,
          topic
        };
      });
    });

    return positions;
  };

  const topicPositions = calculatePositions();

  // Calculate SVG dimensions
  const calculateDimensions = () => {
    let maxX = 0;
    let maxY = 0;

    Object.values(topicPositions).forEach(({ x, y }) => {
      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
    });

    return {
      width: maxX + 300,
      height: maxY + 200
    };
  };

  const { width, height } = calculateDimensions();

  // Draw arrow between two topics
  const renderArrow = (from, to, reason, index) => {
    const fromPos = topicPositions[from];
    const toPos = topicPositions[to];

    if (!fromPos || !toPos) return null;

    // Start from right edge of source hexagon
    const startX = fromPos.x + HEXAGON_SIZE / 2;
    const startY = fromPos.y;

    // End at left edge of target hexagon
    const endX = toPos.x - HEXAGON_SIZE / 2;
    const endY = toPos.y;

    // Bezier curve control points
    const controlX1 = startX + (endX - startX) / 3;
    const controlY1 = startY;
    const controlX2 = startX + (2 * (endX - startX)) / 3;
    const controlY2 = endY;

    const pathData = `M ${startX} ${startY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${endX} ${endY}`;

    // Arrow head
    const arrowSize = 10;
    const angle = Math.atan2(endY - controlY2, endX - controlX2);
    const arrowX1 = endX - arrowSize * Math.cos(angle - Math.PI / 6);
    const arrowY1 = endY - arrowSize * Math.sin(angle - Math.PI / 6);
    const arrowX2 = endX - arrowSize * Math.cos(angle + Math.PI / 6);
    const arrowY2 = endY - arrowSize * Math.sin(angle + Math.PI / 6);

    return (
      <g key={`arrow-${index}-${from}-${to}`} className="dependency-arrow">
        <path
          d={pathData}
          fill="none"
          stroke="#374151"
          strokeWidth="3"
          className="arrow-path"
        />
        <polygon
          points={`${endX},${endY} ${arrowX1},${arrowY1} ${arrowX2},${arrowY2}`}
          fill="#374151"
          className="arrow-head"
        />
        {reason && <title>{reason}</title>}
      </g>
    );
  };

  if (!stages || stages.length === 0) {
    return (
      <div className="staged-tree-empty">
        <p>No learning path stages available</p>
      </div>
    );
  }

  return (
    <div className={`staged-tree-layout ${className}`}>
      <div className="tree-container">
        <svg
          className="tree-canvas"
          width={width}
          height={height}
          viewBox={`0 0 ${width} ${height}`}
        >
          {/* Draw arrows first (background layer) */}
          <g className="arrows-layer">
            {dependencies && dependencies.map((dep, index) =>
              renderArrow(dep.from, dep.to, dep.reason, index)
            )}
          </g>

          {/* Draw hexagons on top */}
          <g className="hexagons-layer">
            {Object.entries(topicPositions).map(([name, { x, y, topic }]) => (
              <g key={`topic-${name}`} transform={`translate(${x}, ${y})`}>
                <foreignObject
                  x={-HEXAGON_SIZE / 2}
                  y={-HEXAGON_SIZE / 2}
                  width={HEXAGON_SIZE}
                  height={HEXAGON_SIZE}
                >
                  <TopicHexagon
                    topic={topic.name}
                    priority={topic.priority}
                    covered={topic.covered !== false}
                    onClick={onTopicClick}
                    size={HEXAGON_SIZE}
                  />
                </foreignObject>
              </g>
            ))}
          </g>
        </svg>
      </div>

      {/* Legend */}
      <div className="tree-legend">
        <div className="legend-item">
          <div className="legend-hexagon high-priority"></div>
          <span>High Priority</span>
        </div>
        <div className="legend-item">
          <div className="legend-hexagon medium-priority"></div>
          <span>Medium Priority</span>
        </div>
        <div className="legend-item">
          <div className="legend-hexagon low-priority"></div>
          <span>Low Priority</span>
        </div>
        <div className="legend-divider"></div>
        <div className="legend-item">
          <div className="legend-border solid"></div>
          <span>Covered in books</span>
        </div>
        <div className="legend-item">
          <div className="legend-border dotted"></div>
          <span>Need resources</span>
        </div>
      </div>
    </div>
  );
};

StagedTreeLayout.propTypes = {
  stages: PropTypes.arrayOf(
    PropTypes.shape({
      stage_number: PropTypes.number.isRequired,
      stage_name: PropTypes.string.isRequired,
      description: PropTypes.string,
      topics: PropTypes.arrayOf(
        PropTypes.shape({
          name: PropTypes.string.isRequired,
          priority: PropTypes.oneOf(['HIGH', 'MEDIUM', 'LOW']),
          covered: PropTypes.bool,
          prerequisites: PropTypes.arrayOf(PropTypes.string)
        })
      )
    })
  ).isRequired,
  dependencies: PropTypes.arrayOf(
    PropTypes.shape({
      from: PropTypes.string.isRequired,
      to: PropTypes.string.isRequired,
      reason: PropTypes.string
    })
  ),
  onTopicClick: PropTypes.func,
  className: PropTypes.string
};

export default StagedTreeLayout;
