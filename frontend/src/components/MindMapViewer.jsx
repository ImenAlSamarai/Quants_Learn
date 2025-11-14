import { useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const MindMapViewer = ({ data, onNodeClick, selectedNode }) => {
  const fgRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const updateDimensions = () => {
      // Ensure finite values for dimensions
      const width = Math.max(window.innerWidth || 800, 400);
      const height = Math.max((window.innerHeight || 680) - 80, 400);

      console.log('Setting dimensions:', { width, height });

      if (!isFinite(width) || !isFinite(height)) {
        console.error('Non-finite dimensions detected, using defaults');
        setDimensions({ width: 800, height: 600 });
      } else {
        setDimensions({ width, height });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Apply custom forces for better layout
  useEffect(() => {
    if (fgRef.current && data.nodes.length > 0) {
      const fg = fgRef.current;

      // Add radial force to spread nodes from center
      fg.d3Force('radial', null); // Remove if exists
      fg.d3Force('charge').strength(-400); // Stronger repulsion
      fg.d3Force('link').distance(150); // Longer links

      // Add collision force to prevent overlap
      fg.d3Force('collision', window.d3.forceCollide(50));

      // Center the graph after physics settle
      setTimeout(() => {
        if (fgRef.current) {
          fgRef.current.zoomToFit(400, 80);
        }
      }, 2000);
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
    const size = 12 + ((difficulty || 1) * 3);
    return isFinite(size) ? size : 15; // Fallback to 15 if not finite
  };

  // Transform data for force-graph with comprehensive validation
  const graphData = {
    nodes: data.nodes.map(node => {
      const isRoot = !data.edges.some(e => e.target === node.id);
      const difficulty = Number(node.difficulty_level) || 1;
      const nodeSize = getNodeSize(difficulty, isRoot);
      const nodeId = Number(node.id);

      // Comprehensive validation
      if (!isFinite(nodeId)) {
        console.error('Invalid node ID:', node.id, node);
        return null;
      }
      if (!isFinite(nodeSize)) {
        console.error('Invalid node size:', nodeSize, node);
        return null;
      }

      return {
        id: nodeId,
        name: String(node.title || 'Untitled'),
        icon: String(node.icon || '📚'),
        difficulty: difficulty,
        description: String(node.description || ''),
        category: String(node.category || ''),
        val: nodeSize,
        color: getNodeColor(difficulty),
        isRoot: isRoot,
      };
    }).filter(Boolean), // Remove any null entries
    links: data.edges.map(edge => {
      const source = Number(edge.source);
      const target = Number(edge.target);

      // Validate link IDs
      if (!isFinite(source) || !isFinite(target)) {
        console.error('Invalid link:', edge);
        return null;
      }

      return {
        source: source,
        target: target,
      };
    }).filter(Boolean),
  };

  // Debug logging
  console.log('Mind map data:', {
    nodeCount: graphData.nodes.length,
    linkCount: graphData.links.length,
    dimensions: dimensions,
    nodes: graphData.nodes,
    links: graphData.links
  });

  const handleNodeClick = (node) => {
    onNodeClick(node);
  };

  // Custom node rendering with labels
  const paintNode = (node, ctx, globalScale) => {
    const label = node.name;
    const fontSize = 14 / globalScale;
    const radius = node.val;

    // Draw node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
    ctx.fillStyle = node.color;
    ctx.fill();

    // Draw border (thicker if selected)
    ctx.strokeStyle = node.id === selectedNode?.id ? '#fbbf24' : '#ffffff';
    ctx.lineWidth = (node.id === selectedNode?.id ? 3 : 2) / globalScale;
    ctx.stroke();

    // Draw icon in center
    ctx.font = `${16 / globalScale}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#ffffff';
    ctx.fillText(node.icon, node.x, node.y);

    // Draw label below node
    ctx.font = `bold ${fontSize}px Sans-Serif`;
    const labelY = node.y + radius + 16 / globalScale;

    // Label background
    const textWidth = ctx.measureText(label).width;
    const padding = 6 / globalScale;
    ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
    ctx.fillRect(
      node.x - textWidth / 2 - padding,
      labelY - fontSize / 2 - padding / 2,
      textWidth + padding * 2,
      fontSize + padding
    );

    // Label text
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, node.x, labelY);
  };

  // Custom link rendering with arrows
  const paintLink = (link, ctx, globalScale) => {
    const start = link.source;
    const end = link.target;

    // Draw link line
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.6)';
    ctx.lineWidth = 2 / globalScale;
    ctx.stroke();

    // Draw arrowhead
    const arrowLength = 10 / globalScale;
    const angle = Math.atan2(end.y - start.y, end.x - start.x);

    ctx.beginPath();
    ctx.moveTo(end.x, end.y);
    ctx.lineTo(
      end.x - arrowLength * Math.cos(angle - Math.PI / 6),
      end.y - arrowLength * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
      end.x - arrowLength * Math.cos(angle + Math.PI / 6),
      end.y - arrowLength * Math.sin(angle + Math.PI / 6)
    );
    ctx.closePath();
    ctx.fillStyle = 'rgba(148, 163, 184, 0.6)';
    ctx.fill();
  };

  console.log('Checking empty state, node count:', data.nodes.length);

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
        nodeCanvasObject={paintNode}
        linkCanvasObject={paintLink}
        onNodeClick={handleNodeClick}
        backgroundColor="#0f172a"
        nodeRelSize={8}
        linkDirectionalArrowLength={0}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
        cooldownTicks={100}
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
