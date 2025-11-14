import { useCallback, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import CustomNode from './CustomNode';
import { colors, edgeStyles, layoutConfig } from './nodeStyles';

const nodeTypes = {
  custom: CustomNode,
};

const MindMapViewerReactflow = ({ data, onNodeClick, selectedNode }) => {
  // Transform backend data to Reactflow format with radial layout
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    if (!data.nodes || data.nodes.length === 0) {
      return { nodes: [], edges: [] };
    }

    // Calculate radial positions
    const categories = layoutConfig.categories;
    const angleStep = (2 * Math.PI) / categories.length;
    const radius = layoutConfig.radius;

    const nodes = data.nodes.map(node => {
      const isRoot = !data.edges.some(e => e.target === node.id);
      const categoryIndex = categories.indexOf(node.category);

      let x, y;
      if (isRoot) {
        // Root nodes at center
        x = layoutConfig.centerX;
        y = layoutConfig.centerY;
      } else {
        // Child nodes in circular clusters around their category position
        const angle = categoryIndex * angleStep;
        const jitter = (Math.random() - 0.5) * 100; // Add some randomness
        x = Math.cos(angle) * radius + jitter;
        y = Math.sin(angle) * radius + jitter;
      }

      return {
        id: String(node.id),
        type: 'custom',
        position: { x, y },
        data: {
          label: node.title,
          icon: node.icon,
          description: node.description,
          category: node.category,
          difficulty: node.difficulty_level,
          isRoot: isRoot,
          originalNode: node,
        },
      };
    });

    const edges = data.edges.map((edge, index) => {
      // Find source and target nodes to determine edge style
      const sourceNode = data.nodes.find(n => n.id === edge.source);
      const targetNode = data.nodes.find(n => n.id === edge.target);

      const sourceDifficulty = sourceNode?.difficulty_level || 1;
      const targetDifficulty = targetNode?.difficulty_level || 1;
      const difficultyGap = Math.abs(targetDifficulty - sourceDifficulty);

      const isDirectPrereq = difficultyGap <= 1;
      const style = isDirectPrereq ? edgeStyles.direct : edgeStyles.indirect;

      return {
        id: `e${edge.source}-${edge.target}-${index}`,
        source: String(edge.source),
        target: String(edge.target),
        type: 'smoothstep',
        animated: isDirectPrereq,
        style: {
          stroke: style.stroke,
          strokeWidth: style.strokeWidth,
          opacity: style.opacity,
          strokeDasharray: style.dashArray,
        },
        markerEnd: {
          type: 'arrowclosed',
          color: style.stroke,
          width: 20,
          height: 20,
        },
      };
    });

    return { nodes, edges };
  }, [data]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onNodeClickHandler = useCallback((event, node) => {
    if (onNodeClick && node.data.originalNode) {
      onNodeClick(node.data.originalNode);
    }
  }, [onNodeClick]);

  // Update selected node styling
  useMemo(() => {
    if (nodes.length > 0) {
      setNodes(nodes.map(node => ({
        ...node,
        selected: selectedNode && String(selectedNode.id) === node.id,
      })));
    }
  }, [selectedNode, setNodes]);

  if (data.nodes.length === 0) {
    return (
      <div className="empty-state">
        <h2>No topics available</h2>
        <p>Select a category or index some content to get started.</p>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '100%', background: colors.background }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClickHandler}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{
          padding: 0.2,
          maxZoom: 1.2,
        }}
        minZoom={0.5}
        maxZoom={2}
        defaultEdgeOptions={{
          type: 'smoothstep',
        }}
      >
        <Background
          color="#E5E7EB"
          gap={20}
          size={1}
          variant="dots"
        />
        <Controls
          showInteractive={false}
          style={{
            background: '#FFFFFF',
            border: '1px solid #E5E7EB',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
          }}
        />
        <MiniMap
          nodeColor={(node) => {
            const category = node.data?.category || 'linear_algebra';
            return colors.categories[category]?.main || '#818CF8';
          }}
          maskColor="rgba(0, 0, 0, 0.05)"
          style={{
            background: '#FFFFFF',
            border: '1px solid #E5E7EB',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
          }}
        />
      </ReactFlow>

      {/* Legend */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        left: '20px',
        background: '#FFFFFF',
        padding: '20px',
        borderRadius: '12px',
        border: '1px solid #E5E7EB',
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        maxWidth: '200px',
        zIndex: 5,
      }}>
        <h4 style={{
          margin: '0 0 12px 0',
          fontSize: '14px',
          fontWeight: '600',
          color: colors.node.text,
        }}>
          Difficulty Levels
        </h4>
        {[1, 2, 3, 4, 5].map(level => (
          <div key={level} style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '8px',
          }}>
            <div style={{
              width: '20px',
              height: '20px',
              borderRadius: '50%',
              background: colors.difficulty[level],
              marginRight: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '10px',
              fontWeight: '700',
              color: '#FFFFFF',
            }}>
              {level}
            </div>
            <span style={{
              fontSize: '12px',
              color: colors.node.textSecondary,
            }}>
              {['Fundamentals', 'Core', 'Intermediate', 'Advanced', 'Expert'][level - 1]}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MindMapViewerReactflow;
