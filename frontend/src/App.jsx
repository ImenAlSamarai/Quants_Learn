import { useState, useEffect } from 'react';
import MindMapViewer from './components/MindMapViewer';
import NodePanel from './components/NodePanel';
import Header from './components/Header';
import AdminPanel from './components/AdminPanel';
import UserSettings from './components/UserSettings';
import { fetchMindMap } from './services/api';

function App() {
  const [mindMapData, setMindMapData] = useState({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userId] = useState('demo_user'); // Simple user tracking for MVP
  const [showAdmin, setShowAdmin] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

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

  // Show admin panel if enabled
  if (showAdmin) {
    return (
      <div className="app">
        <div style={{
          position: 'fixed',
          top: '1.25rem',
          right: '2rem',
          zIndex: 1000
        }}>
          <button
            onClick={() => setShowAdmin(false)}
            style={{
              background: 'rgba(51, 65, 85, 0.5)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              color: '#f1f5f9',
              border: '1px solid rgba(148, 163, 184, 0.3)',
              padding: '0.75rem 1.5rem',
              borderRadius: '12px',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              fontSize: '0.9rem'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 8px 30px rgba(59, 130, 246, 0.3)';
              e.target.style.borderColor = 'rgba(59, 130, 246, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
              e.target.style.borderColor = 'rgba(148, 163, 184, 0.3)';
            }}
          >
            ← Back to Learning
          </button>
        </div>
        <AdminPanel />
      </div>
    );
  }

  return (
    <div className="app">
      <Header
        categories={categories}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
      />

      <div style={{
        position: 'fixed',
        top: '1.25rem',
        right: '2rem',
        zIndex: 1000,
        display: 'flex',
        gap: '0.75rem'
      }}>
        <button
          onClick={() => setShowSettings(true)}
          style={{
            background: 'rgba(51, 65, 85, 0.5)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            color: '#f1f5f9',
            border: '1px solid rgba(148, 163, 184, 0.3)',
            padding: '0.75rem 1.5rem',
            borderRadius: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            fontSize: '0.9rem'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 8px 30px rgba(59, 130, 246, 0.3)';
            e.target.style.borderColor = 'rgba(59, 130, 246, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
            e.target.style.borderColor = 'rgba(148, 163, 184, 0.3)';
          }}
        >
          ⚙️ Settings
        </button>
        <button
          onClick={() => setShowAdmin(true)}
          style={{
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.8) 0%, rgba(139, 92, 246, 0.8) 100%)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            color: 'white',
            border: '1px solid rgba(59, 130, 246, 0.5)',
            padding: '0.75rem 1.5rem',
            borderRadius: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(59, 130, 246, 0.3)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            fontSize: '0.9rem'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 8px 40px rgba(59, 130, 246, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 4px 20px rgba(59, 130, 246, 0.3)';
          }}
        >
          📊 Admin Panel
        </button>
      </div>

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

        {showSettings && (
          <UserSettings
            userId={userId}
            onClose={() => setShowSettings(false)}
          />
        )}
      </div>
    </div>
  );
}

export default App;
