import React, { useRef, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import TopicHexagon from './TopicHexagon';
import './StagedTreeLayout.css';

/**
 * StagedTreeLayout - Horizontal tree visualization with stages
 *
 * Layout: Foundations → Core Skills → Advanced Applications
 * - Hexagons arranged in stages (left to right)
 * - Dependency arrows showing prerequisites
 * - Color-coded by priority
 * - Dotted borders for uncovered topics
 */
const StagedTreeLayout = ({
  stages = [],
  dependencies = [],
  onTopicClick,
  className = ''
}) => {
  const svgRef = useRef(null);
  const [hexagonPositions, setHexagonPositions] = useState({});
  const [svgDimensions, setSvgDimensions] = useState({ width: 0, height: 0 });

  const HEXAGON_SIZE = 140;
  const STAGE_SPACING = 280; // Horizontal spacing between stages
  const TOPIC_SPACING = 160; // Vertical spacing between topics in same stage

  // Calculate positions for all hexagons
  useEffect(() => {
    if (!stages || stages.length === 0) return;

    const positions = {};
    let maxHeight = 0;

    stages.forEach((stage, stageIndex) => {
      const topics = stage.topics || [];
      const stageHeight = topics.length * TOPIC_SPACING;
      const stageX = stageIndex * STAGE_SPACING + HEXAGON_SIZE;

      topics.forEach((topic, topicIndex) => {
        const key = topic.name;
        const x = stageX;
        const y = topicIndex * TOPIC_SPACING + HEXAGON_SIZE;

        positions[key] = { x, y, topic };
        maxHeight = Math.max(maxHeight, y + HEXAGON_SIZE);
      });
    });

    setHexagonPositions(positions);
    setSvgDimensions({
      width: stages.length * STAGE_SPACING + HEXAGON_SIZE * 2,
      height: maxHeight + HEXAGON_SIZE
    });
  }, [stages]);

  // Draw arrow between two topics
  const drawArrow = (from, to, reason) => {
    const fromPos = hexagonPositions[from];
    const toPos = hexagonPositions[to];

    if (!fromPos || !toPos) return null;

    const startX = fromPos.x + HEXAGON_SIZE / 2;
    const startY = fromPos.y + HEXAGON_SIZE / 2;
    const endX = toPos.x - HEXAGON_SIZE / 2 - 10;
    const endY = toPos.y + HEXAGON_SIZE / 2;

    // Bezier curve for smooth arrow
    const controlX1 = startX + (endX - startX) / 3;
    const controlY1 = startY;
    const controlX2 = startX + (2 * (endX - startX)) / 3;
    const controlY2 = endY;

    const pathData = `M ${startX} ${startY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${endX} ${endY}`;

    // Arrow head
    const arrowSize = 8;
    const angle = Math.atan2(endY - controlY2, endX - controlX2);
    const arrowX1 = endX - arrowSize * Math.cos(angle - Math.PI / 6);
    const arrowY1 = endY - arrowSize * Math.sin(angle - Math.PI / 6);
    const arrowX2 = endX - arrowSize * Math.cos(angle + Math.PI / 6);
    const arrowY2 = endY - arrowSize * Math.sin(angle + Math.PI / 6);

    return (
      <g key={`arrow-${from}-${to}`} className="dependency-arrow">
        <path
          d={pathData}
          fill="none"
          stroke="#374151"
          strokeWidth="4"
          className="arrow-path"
        />
        <polygon
          points={`${endX},${endY} ${arrowX1},${arrowY1} ${arrowX2},${arrowY2}`}
          fill="#374151"
          className="arrow-head"
        />
        {reason && (
          <title>{reason}</title>
        )}
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
      {/* SVG canvas for hexagons and arrows */}
      <svg
        ref={svgRef}
        className="tree-canvas"
        width={svgDimensions.width}
        height={svgDimensions.height}
        style={{ minHeight: '400px' }}
      >
        {/* Arrow marker definition */}
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 10 3, 0 6" fill="#9CA3AF" />
          </marker>
        </defs>

        {/* Draw hexagons first (background) */}
        {Object.entries(hexagonPositions).map(([key, { x, y, topic }]) => (
          <g
            key={`hex-${key}`}
            transform={`translate(${x - HEXAGON_SIZE / 2}, ${y - HEXAGON_SIZE / 2})`}
          >
            <foreignObject
              width={HEXAGON_SIZE}
              height={HEXAGON_SIZE}
              className="hexagon-container"
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

        {/* Draw dependency arrows on top */}
        {dependencies && dependencies.map((dep) =>
          drawArrow(dep.from, dep.to, dep.reason)
        )}
      </svg>

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
