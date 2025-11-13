import { useState, useEffect } from 'react';
import MindMapViewer from './components/MindMapViewer';
import NodePanel from './components/NodePanel';
import Header from './components/Header';
import { fetchMindMap } from './services/api';

function App() {
  const [mindMapData, setMindMapData] = useState({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userId] = useState('demo_user'); // Simple user tracking for MVP

  useEffect(() => {
    loadMindMap();
  }, [selectedCategory]);

  const loadMindMap = async () => {
    setLoading(true);
    try {
      const data = await fetchMindMap(selectedCategory);
      setMindMapData(data);
    } catch (error) {
      console.error('Error loading mind map:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
  };

  const handleClosePanel = () => {
    setSelectedNode(null);
  };

  const categories = [
    { id: 'linear_algebra', name: 'Linear Algebra', icon: '🔷', color: '#3b82f6' },
    { id: 'calculus', name: 'Calculus', icon: '∫', color: '#10b981' },
    { id: 'probability', name: 'Probability', icon: '🎲', color: '#f59e0b' },
    { id: 'statistics', name: 'Statistics', icon: '📊', color: '#8b5cf6' },
  ];

  return (
    <div className="app">
      <Header
        categories={categories}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
      />

      <div className="main-content">
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading mind map...</p>
          </div>
        ) : (
          <MindMapViewer
            data={mindMapData}
            onNodeClick={handleNodeClick}
            selectedNode={selectedNode}
          />
        )}

        {selectedNode && (
          <NodePanel
            node={selectedNode}
            userId={userId}
            onClose={handleClosePanel}
          />
        )}
      </div>
    </div>
  );
}

export default App;
