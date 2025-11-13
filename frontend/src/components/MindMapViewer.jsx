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
          fgRef.current.zoomToFit(400, 50);
        }
      }, 500);
    }
  }, [data]);

  // Transform data for force-graph
  const graphData = {
    nodes: data.nodes.map(node => ({
      id: node.id,
      name: node.title,
      icon: node.icon || '📚',
      color: node.color || '#3b82f6',
      difficulty: node.difficulty_level || 1,
      category: node.category,
      val: 10 + (node.difficulty_level || 1) * 2, // Node size
      ...node,
    })),
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
    const fontSize = 14 / globalScale;
    const iconSize = 20 / globalScale;

    // Draw node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI, false);
    ctx.fillStyle = node.id === selectedNode?.id ? '#fbbf24' : node.color;
    ctx.fill();

    // Draw border
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2 / globalScale;
    ctx.stroke();

    // Draw icon
    ctx.font = `${iconSize}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#fff';
    ctx.fillText(node.icon, node.x, node.y);

    // Draw label below node
    ctx.font = `${fontSize}px Sans-Serif`;
    ctx.fillStyle = '#fff';
    ctx.fillText(label, node.x, node.y + node.val + 8 / globalScale);

    // Draw difficulty indicator
    const stars = '⭐'.repeat(node.difficulty || 1);
    ctx.font = `${fontSize * 0.7}px Sans-Serif`;
    ctx.fillText(stars, node.x, node.y + node.val + 20 / globalScale);
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

    // Draw arrow
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 2 / globalScale;
    ctx.stroke();

    // Draw arrowhead
    const angle = Math.atan2(end.y - start.y, end.x - start.x);
    const arrowLength = 10 / globalScale;
    const arrowWidth = 6 / globalScale;

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
    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
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
            Difficulty: ${'⭐'.repeat(node.difficulty || 1)}<br/>
            ${node.description || ''}
          </div>
        `}
        nodeCanvasObject={paintNode}
        nodePointerAreaPaint={nodePointerAreaPaint}
        linkCanvasObject={paintLink}
        onNodeClick={handleNodeClick}
        nodeRelSize={1}
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        linkWidth={2}
        backgroundColor="#0f172a"
        cooldownTicks={100}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
        enableNodeDrag={true}
        enableZoomInteraction={true}
        enablePanInteraction={true}
      />

      <div className="controls-overlay">
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
