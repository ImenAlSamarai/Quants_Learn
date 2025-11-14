import { useRef, useEffect, useState, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { forceX, forceY } from 'd3-force';
import { MousePointer2, ZoomIn, Move } from 'lucide-react';

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

  // Color scheme based on difficulty level - Claude-inspired Light Theme
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

  // Node size scales with complexity
  const getNodeSize = (difficulty, isRoot = false) => {
    if (isRoot) return 25;
    const size = 12 + ((difficulty || 1) * 3);
    return isFinite(size) ? size : 15; // Fallback to 15 if not finite
  };

  // Transform data for force-graph with comprehensive validation (memoized)
  const graphData = useMemo(() => ({
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
  }), [data]);

  // Apply radial cluster layout forces
  useEffect(() => {
    if (fgRef.current && data.nodes.length > 0) {
      const fg = fgRef.current;

      // Radial: Category-based circular clusters
      fg.d3Force('charge').strength(-200);
      fg.d3Force('link').distance(100);

      // Position categories in a circle using forceX and forceY
      const categories = ['linear_algebra', 'calculus', 'probability', 'statistics'];
      const angleStep = (2 * Math.PI) / categories.length;
      const radius = 300;

      fg.d3Force('category-x', forceX().strength(0.5).x(d => {
        const index = categories.indexOf(d.category);
        if (d.isRoot) return 0;
        return Math.cos(index * angleStep) * radius;
      }));

      fg.d3Force('category-y', forceY().strength(0.5).y(d => {
        const index = categories.indexOf(d.category);
        if (d.isRoot) return 0;
        return Math.sin(index * angleStep) * radius;
      }));

      // Center the graph after physics settle
      setTimeout(() => {
        if (fgRef.current) {
          fgRef.current.zoomToFit(400, 80);
        }
      }, 2000);
    }
  }, [data, graphData]);

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
    ctx.strokeStyle = node.id === selectedNode?.id ? '#C9A96E' : '#1A1A1A';
    ctx.lineWidth = (node.id === selectedNode?.id ? 3 : 2) / globalScale;
    ctx.stroke();

    // Draw icon in center
    ctx.font = `${16 / globalScale}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(node.icon, node.x, node.y);

    // Draw label below node
    ctx.font = `bold ${fontSize}px 'Inter', sans-serif`;
    const labelY = node.y + radius + 16 / globalScale;

    // Label background
    const textWidth = ctx.measureText(label).width;
    const padding = 6 / globalScale;
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.fillRect(
      node.x - textWidth / 2 - padding,
      labelY - fontSize / 2 - padding / 2,
      textWidth + padding * 2,
      fontSize + padding
    );

    // Label text
    ctx.fillStyle = '#1A1A1A';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, node.x, labelY);
  };

  // Custom link rendering with curved arrows and varying styles
  const paintLink = (link, ctx, globalScale) => {
    const start = link.source;
    const end = link.target;

    // Calculate midpoint for curved path
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Create curved path (quadratic curve)
    const curvature = 0.25;
    const controlX = start.x + dx * 0.5 - dy * curvature;
    const controlY = start.y + dy * 0.5 + dx * curvature;

    // Determine link strength based on difficulty difference
    const sourceDifficulty = start.difficulty || 1;
    const targetDifficulty = end.difficulty || 1;
    const difficultyGap = Math.abs(targetDifficulty - sourceDifficulty);

    // Direct prerequisites (same or +1 difficulty) = thick solid line
    // Larger gaps = thinner, more transparent (indirect/optional)
    const isDirectPrereq = difficultyGap <= 1;
    const lineWidth = isDirectPrereq ? 2.5 / globalScale : 1.5 / globalScale;
    const opacity = isDirectPrereq ? 0.8 : 0.4;

    // Color based on target difficulty
    const targetColor = end.color || '#3b82f6';

    // Draw curved line
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.quadraticCurveTo(controlX, controlY, end.x, end.y);
    ctx.strokeStyle = `${targetColor}${Math.floor(opacity * 255).toString(16).padStart(2, '0')}`;
    ctx.lineWidth = lineWidth;

    // Dashed for optional/indirect paths
    if (!isDirectPrereq) {
      ctx.setLineDash([5 / globalScale, 5 / globalScale]);
    } else {
      ctx.setLineDash([]);
    }

    ctx.stroke();
    ctx.setLineDash([]); // Reset

    // Draw arrowhead at the end
    const arrowLength = isDirectPrereq ? 12 / globalScale : 8 / globalScale;
    const arrowWidth = isDirectPrereq ? 8 / globalScale : 6 / globalScale;

    // Calculate angle at the end of the curve
    const angle = Math.atan2(end.y - controlY, end.x - controlX);

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
    ctx.fillStyle = `${targetColor}${Math.floor(opacity * 255).toString(16).padStart(2, '0')}`;
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
        backgroundColor="#FAF9F6"
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
          <h4>Difficulty Levels</h4>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#7BA591' }}></span>
            <span>Fundamentals</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#6B9BD1' }}></span>
            <span>Core Concepts</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#9B8FB5' }}></span>
            <span>Intermediate</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#D4A574' }}></span>
            <span>Advanced</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#C17B6C' }}></span>
            <span>Expert</span>
          </div>

          <h4 style={{ marginTop: '1.25rem' }}>Connections</h4>
          <div className="legend-item">
            <span style={{
              display: 'inline-block',
              width: '28px',
              height: '2.5px',
              backgroundColor: '#6B6B6B',
              borderRadius: '2px',
              flexShrink: 0
            }}></span>
            <span>Direct prerequisite</span>
          </div>
          <div className="legend-item">
            <span style={{
              display: 'inline-block',
              width: '28px',
              height: '2px',
              backgroundColor: '#9B9B9B',
              borderRadius: '2px',
              flexShrink: 0,
              backgroundImage: 'linear-gradient(to right, #9B9B9B 50%, transparent 50%)',
              backgroundSize: '6px 2px'
            }}></span>
            <span>Related/Optional</span>
          </div>
        </div>
        <div className="control-hint">
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <MousePointer2 size={14} />
            <span>Click nodes to explore</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ZoomIn size={14} />
            <span>Scroll to zoom</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Move size={14} />
            <span>Drag nodes to arrange</span>
          </span>
        </div>
      </div>
    </div>
  );
};

export default MindMapViewer;
