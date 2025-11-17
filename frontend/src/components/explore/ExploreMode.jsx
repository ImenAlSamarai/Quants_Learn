import { useRef, useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import ForceGraph2D from 'react-force-graph-2d';
import { forceX, forceY, forceCollide } from 'd3-force';
import { MousePointer2, ZoomIn, Move } from 'lucide-react';
import { motion } from 'framer-motion';
import useAppStore from '../../store/useAppStore';

// Color scheme based on difficulty level
const getNodeColor = (difficulty) => {
  const colors = {
    1: '#7BA591', // Sage - Fundamentals
    2: '#6B9BD1', // Ocean - Core Concepts
    3: '#9B8FB5', // Lavender - Intermediate
    4: '#D4A574', // Tan - Advanced
    5: '#C17B6C', // Terracotta - Expert
  };
  return colors[difficulty] || '#7BA591';
};

const ExploreMode = ({ categoryId }) => {
  const navigate = useNavigate();
  const graphRef = useRef();
  const [selectedNode, setSelectedNode] = useState(null);
  const { topics, completedTopics } = useAppStore();

  // Filter topics for current category
  const categoryTopics = useMemo(() => {
    return topics.filter((topic) => topic.category === categoryId);
  }, [topics, categoryId]);

  // Create graph data
  const graphData = useMemo(() => {
    const nodes = categoryTopics.map((topic) => ({
      id: topic.id,
      name: topic.name,
      icon: topic.icon,
      difficulty: topic.difficulty,
      color: getNodeColor(topic.difficulty),
      val: 8 + (topic.difficulty || 1) * 2, // Smaller nodes: 10-18px radius
      completed: completedTopics.includes(topic.id),
    }));

    const links = [];
    categoryTopics.forEach((topic) => {
      if (topic.prerequisites) {
        topic.prerequisites.forEach((prereqId) => {
          if (categoryTopics.find((t) => t.id === prereqId)) {
            links.push({
              source: prereqId,
              target: topic.id,
              value: 1,
            });
          }
        });
      }
    });

    return { nodes, links };
  }, [categoryTopics, completedTopics]);

  // Custom node rendering
  const paintNode = (node, ctx, globalScale) => {
    const label = node.name;
    const fontSize = 14 / globalScale;
    const radius = node.val;

    // Draw shadow
    ctx.beginPath();
    ctx.arc(node.x, node.y + 2 / globalScale, radius, 0, 2 * Math.PI, false);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fill();

    // Draw node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
    ctx.fillStyle = node.color;
    ctx.fill();

    // Draw completion ring
    if (node.completed) {
      ctx.strokeStyle = '#C9A96E';
      ctx.lineWidth = 3 / globalScale;
      ctx.stroke();
    }

    // Draw border
    ctx.strokeStyle =
      node.id === selectedNode?.id ? '#C9A96E' : 'rgba(26, 26, 26, 0.6)';
    ctx.lineWidth = (node.id === selectedNode?.id ? 3 : 1.5) / globalScale;
    ctx.stroke();

    // Draw icon (bigger and more visible)
    ctx.font = `${24 / globalScale}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(node.icon, node.x, node.y);

    // Draw label
    ctx.font = `600 ${fontSize}px 'Inter', sans-serif`;
    const labelY = node.y + radius + 16 / globalScale;
    const textWidth = ctx.measureText(label).width;
    const padding = 8 / globalScale;

    // Label shadow
    ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
    ctx.fillRect(
      node.x - textWidth / 2 - padding + 1 / globalScale,
      labelY - fontSize / 2 - padding / 2 + 1 / globalScale,
      textWidth + padding * 2,
      fontSize + padding
    );

    // Label background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.98)';
    ctx.fillRect(
      node.x - textWidth / 2 - padding,
      labelY - fontSize / 2 - padding / 2,
      textWidth + padding * 2,
      fontSize + padding
    );

    // Label text
    ctx.fillStyle = '#1A1A1A';
    ctx.fillText(label, node.x, labelY);
  };

  // Custom link rendering
  const paintLink = (link, ctx, globalScale) => {
    const start = link.source;
    const end = link.target;

    // Draw link with better visibility
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.strokeStyle = 'rgba(107, 107, 107, 0.6)'; // More visible
    ctx.lineWidth = 1.5 / globalScale;
    ctx.stroke();

    // Draw arrow
    const arrowLength = 8 / globalScale;
    const angle = Math.atan2(end.y - start.y, end.x - start.x);
    const endRadius = end.val || 10;

    const arrowX = end.x - Math.cos(angle) * endRadius;
    const arrowY = end.y - Math.sin(angle) * endRadius;

    ctx.beginPath();
    ctx.moveTo(arrowX, arrowY);
    ctx.lineTo(
      arrowX - arrowLength * Math.cos(angle - Math.PI / 6),
      arrowY - arrowLength * Math.sin(angle - Math.PI / 6)
    );
    ctx.moveTo(arrowX, arrowY);
    ctx.lineTo(
      arrowX - arrowLength * Math.cos(angle + Math.PI / 6),
      arrowY - arrowLength * Math.sin(angle + Math.PI / 6)
    );
    ctx.strokeStyle = 'rgba(107, 107, 107, 0.7)'; // More visible
    ctx.lineWidth = 1.5 / globalScale;
    ctx.stroke();
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    navigate(`/category/${categoryId}/topic/${node.id}`);
  };

  const handleBackgroundClick = () => {
    setSelectedNode(null);
  };

  useEffect(() => {
    if (graphRef.current) {
      // Add radial force for better layout
      graphRef.current.d3Force(
        'radial',
        forceX(0).strength(0.05)
      );
      graphRef.current.d3Force(
        'radial-y',
        forceY(0).strength(0.05)
      );

      // Add stronger collision to prevent overlapping
      graphRef.current.d3Force('collide', null); // Remove default
      graphRef.current.d3Force('collision',
        forceCollide().radius((node) => (node.val || 10) + 20).strength(0.9)
      );

      // Zoom to fit with padding
      setTimeout(() => {
        graphRef.current?.zoomToFit(400, 80);
      }, 500);
    }
  }, [graphData]);

  return (
    <motion.div
      className="explore-mode"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      <div className="explore-container">
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          backgroundColor="#FAF9F6"
          nodeLabel={(node) => node.name}
          nodeCanvasObject={paintNode}
          linkCanvasObject={paintLink}
          onNodeClick={handleNodeClick}
          onBackgroundClick={handleBackgroundClick}
          enableNodeDrag={true}
          cooldownTime={3000}
          d3AlphaDecay={0.02}
          d3VelocityDecay={0.3}
        />
      </div>

      {/* Legend */}
      <div className="explore-legend">
        <h4 className="legend-title">Difficulty Levels</h4>
        <div className="legend-items">
          {[
            { level: 1, label: 'Fundamentals', color: '#7BA591' },
            { level: 2, label: 'Core Concepts', color: '#6B9BD1' },
            { level: 3, label: 'Intermediate', color: '#9B8FB5' },
            { level: 4, label: 'Advanced', color: '#D4A574' },
            { level: 5, label: 'Expert', color: '#C17B6C' },
          ].map((item) => (
            <div key={item.level} className="legend-item">
              <span
                className="legend-dot"
                style={{ backgroundColor: item.color }}
              />
              <span className="legend-label">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Controls Hint */}
      <div className="explore-hints">
        <span className="hint-item">
          <MousePointer2 size={14} />
          <span>Click to study</span>
        </span>
        <span className="hint-item">
          <ZoomIn size={14} />
          <span>Scroll to zoom</span>
        </span>
        <span className="hint-item">
          <Move size={14} />
          <span>Drag to arrange</span>
        </span>
      </div>
    </motion.div>
  );
};

export default ExploreMode;
