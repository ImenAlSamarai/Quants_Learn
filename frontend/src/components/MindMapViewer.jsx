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

  // Temporarily disabled zoomToFit for debugging
  // useEffect(() => {
  //   if (fgRef.current && data.nodes.length > 0) {
  //     setTimeout(() => {
  //       if (fgRef.current) {
  //         fgRef.current.zoomToFit(400, 100);
  //       }
  //     }, 1000);
  //   }
  // }, [data]);

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
        val: nodeSize,
        color: getNodeColor(difficulty),
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
        nodeLabel="name"
        onNodeClick={handleNodeClick}
        nodeAutoColorBy="color"
        backgroundColor="#0f172a"
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
