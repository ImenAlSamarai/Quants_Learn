import { useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const MindMapViewer = ({ data, onNodeClick, selectedNode }) => {
  const fgRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight - 80, // Account for header
      });
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    // Center the graph on mount with a delay to ensure rendering
    if (fgRef.current && data.nodes.length > 0) {
      setTimeout(() => {
        if (fgRef.current) {
          fgRef.current.zoomToFit(400, 100);
        }
      }, 1000);
    }
  }, [data]);

  // Color scheme based on difficulty level
  const getNodeColor = (difficulty) => {
    const colors = {
      1: '#10b981', // Green - Fundamentals
      2: '#3b82f6', // Blue - Core Concepts
      3: '#8b5cf6', // Purple - Intermediate
      4: '#ec4899', // Pink - Advanced
      5: '#ef4444', // Red - Expert
    };
    return colors[difficulty] || '#3b82f6';
  };

  // Node size scales with complexity
  const getNodeSize = (difficulty, isRoot = false) => {
    if (isRoot) return 25;
    return 12 + (difficulty * 3);
  };

  // Transform data for force-graph with enhanced styling
  const graphData = {
    nodes: data.nodes.map(node => {
      const isRoot = !data.edges.some(e => e.target === node.id);
      const difficulty = node.difficulty_level || 1;

      return {
        id: node.id,
        name: node.title,
        icon: node.icon || '📚',
        color: getNodeColor(difficulty),
        difficulty: difficulty,
        category: node.category,
        val: getNodeSize(difficulty, isRoot),
        isRoot: isRoot,
        ...node,
      };
    }),
    links: data.edges.map(edge => ({
      source: edge.source,
      target: edge.target,
      type: edge.type || 'prerequisite',
    })),
  };

  const handleNodeClick = (node) => {
    onNodeClick(node);
  };

  const paintNode = (node, ctx, globalScale) => {
    const label = node.name;
    const fontSize = node.isRoot ? 16 / globalScale : 14 / globalScale;
    const iconSize = node.isRoot ? 24 / globalScale : 20 / globalScale;
    const radius = node.val;

    // Draw glow effect for selected node
    if (node.id === selectedNode?.id) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, radius + 4 / globalScale, 0, 2 * Math.PI, false);
      const gradient = ctx.createRadialGradient(node.x, node.y, radius, node.x, node.y, radius + 4 / globalScale);
      gradient.addColorStop(0, node.color + 'FF');
      gradient.addColorStop(1, node.color + '00');
      ctx.fillStyle = gradient;
      ctx.fill();
    }

    // Draw node circle with gradient
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);

    // Create gradient for depth
    const gradient = ctx.createRadialGradient(
      node.x - radius * 0.3,
      node.y - radius * 0.3,
      radius * 0.1,
      node.x,
      node.y,
      radius
    );

    if (node.id === selectedNode?.id) {
      gradient.addColorStop(0, '#fbbf24');
      gradient.addColorStop(1, '#f59e0b');
    } else {
      const lightColor = node.color + 'FF';
      const darkColor = node.color + 'CC';
      gradient.addColorStop(0, lightColor);
      gradient.addColorStop(1, darkColor);
    }

    ctx.fillStyle = gradient;
    ctx.fill();

    // Draw border
    ctx.strokeStyle = node.id === selectedNode?.id ? '#fbbf24' : '#fff';
    ctx.lineWidth = node.isRoot ? 3 / globalScale : 2 / globalScale;
    ctx.stroke();

    // Draw inner ring for root nodes
    if (node.isRoot) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, radius * 0.7, 0, 2 * Math.PI, false);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
      ctx.lineWidth = 1 / globalScale;
      ctx.stroke();
    }

    // Draw icon
    ctx.font = `${iconSize}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#fff';
    ctx.fillText(node.icon, node.x, node.y);

    // Draw label below node with background
    ctx.font = `bold ${fontSize}px Sans-Serif`;
    const labelWidth = ctx.measureText(label).width;
    const labelPadding = 6 / globalScale;
    const labelY = node.y + radius + 20 / globalScale;

    // Label background
    ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
    ctx.fillRect(
      node.x - labelWidth / 2 - labelPadding,
      labelY - fontSize / 2 - labelPadding / 2,
      labelWidth + labelPadding * 2,
      fontSize + labelPadding
    );

    // Label text
    ctx.fillStyle = '#fff';
    ctx.fillText(label, node.x, labelY);

    // Draw difficulty indicator with level name
    const difficultyLabels = {
      1: 'Fundamentals',
      2: 'Core',
      3: 'Intermediate',
      4: 'Advanced',
      5: 'Expert'
    };

    const difficultyText = difficultyLabels[node.difficulty] || 'Core';
    ctx.font = `${fontSize * 0.65}px Sans-Serif`;
    ctx.fillStyle = node.color;
    ctx.fillText(difficultyText, node.x, labelY + fontSize + 6 / globalScale);
  };

  const nodePointerAreaPaint = (node, color, ctx) => {
    // Define clickable area
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI, false);
    ctx.fill();
  };

  const paintLink = (link, ctx, globalScale) => {
    const start = link.source;
    const end = link.target;

    // Calculate control points for curved path
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Create curved path
    const curvature = 0.2;
    const controlX = start.x + dx * 0.5 - dy * curvature;
    const controlY = start.y + dy * 0.5 + dx * curvature;

    // Draw arrow with gradient
    const gradient = ctx.createLinearGradient(start.x, start.y, end.x, end.y);
    gradient.addColorStop(0, 'rgba(139, 92, 246, 0.3)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.5)');

    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.quadraticCurveTo(controlX, controlY, end.x, end.y);
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 2 / globalScale;
    ctx.stroke();

    // Draw arrowhead
    const angle = Math.atan2(end.y - controlY, end.x - controlX);
    const arrowLength = 12 / globalScale;
    const arrowWidth = 8 / globalScale;

    ctx.beginPath();
    ctx.moveTo(end.x, end.y);
    ctx.lineTo(
      end.x - arrowLength * Math.cos(angle - Math.PI / 7),
      end.y - arrowLength * Math.sin(angle - Math.PI / 7)
    );
    ctx.lineTo(
      end.x - arrowLength * Math.cos(angle + Math.PI / 7),
      end.y - arrowLength * Math.sin(angle + Math.PI / 7)
    );
    ctx.closePath();
    ctx.fillStyle = 'rgba(139, 92, 246, 0.6)';
    ctx.fill();
  };

  if (data.nodes.length === 0) {
    return (
      <div className="empty-state">
        <h2>No topics available</h2>
        <p>Select a category or index some content to get started.</p>
      </div>
    );
  }

  return (
    <div className="mind-map-container">
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        width={dimensions.width}
        height={dimensions.height}
        nodeLabel={node => `
          <div class="node-tooltip">
            <strong>${node.icon} ${node.name}</strong><br/>
            <span style="color: ${node.color}">
              ${node.difficulty === 1 ? 'Fundamentals' :
                node.difficulty === 2 ? 'Core Concepts' :
                node.difficulty === 3 ? 'Intermediate' :
                node.difficulty === 4 ? 'Advanced' : 'Expert'}
            </span><br/>
            ${node.description || ''}
          </div>
        `}
        nodeCanvasObject={paintNode}
        nodePointerAreaPaint={nodePointerAreaPaint}
        linkCanvasObject={paintLink}
        onNodeClick={handleNodeClick}
        dagMode="td"
        dagLevelDistance={100}
        nodeRelSize={1}
        linkDirectionalArrowLength={0}
        linkDirectionalArrowRelPos={1}
        linkWidth={2}
        linkCurvature={0.2}
        backgroundColor="#0f172a"
        cooldownTicks={100}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
        enableNodeDrag={true}
        enableZoomInteraction={true}
        enablePanInteraction={true}
      />

      <div className="controls-overlay">
        <div className="legend">
          <h4>Learning Path</h4>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#10b981' }}></span>
            <span>Fundamentals</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#3b82f6' }}></span>
            <span>Core Concepts</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#8b5cf6' }}></span>
            <span>Intermediate</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#ec4899' }}></span>
            <span>Advanced</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#ef4444' }}></span>
            <span>Expert</span>
          </div>
        </div>
        <div className="control-hint">
          <span>🖱️ Click nodes to explore</span>
          <span>🔍 Scroll to zoom</span>
          <span>✋ Drag to pan</span>
        </div>
      </div>
    </div>
  );
};

export default MindMapViewer;
