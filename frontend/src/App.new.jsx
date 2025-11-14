import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Header from './components/layout/Header';
import LandingPage from './pages/LandingPage';
import CategoryView from './pages/CategoryView';
import AdminPanel from './components/AdminPanel';
import UserSettings from './components/UserSettings';
import useAppStore from './store/useAppStore';
import { fetchMindMap } from './services/api';

function App() {
  const [loading, setLoading] = useState(true);
  const [userId] = useState('demo_user');
  const [showAdmin, setShowAdmin] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const { setCategories, setTopics } = useAppStore();

  // Define categories
  const categories = [
    {
      id: 'linear_algebra',
      name: 'Linear Algebra',
      icon: '📐',
      description: 'Master vectors, matrices, and linear transformations essential for quant finance',
      difficulty: 2,
    },
    {
      id: 'calculus',
      name: 'Calculus',
      icon: '📈',
      description: 'Understand derivatives, integrals, and optimization techniques',
      difficulty: 3,
    },
    {
      id: 'probability',
      name: 'Probability',
      icon: '🎲',
      description: 'Learn probability theory, distributions, and stochastic processes',
      difficulty: 3,
    },
    {
      id: 'statistics',
      name: 'Statistics',
      icon: '📊',
      description: 'Statistical inference, hypothesis testing, and regression analysis',
      difficulty: 2,
    },
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load all categories' data
      const allTopics = [];

      for (const category of categories) {
        const data = await fetchMindMap(category.id);

        // Transform nodes to topics
        if (data.nodes) {
          const categoryTopics = data.nodes.map((node) => ({
            id: node.id,
            name: node.name,
            description: node.description || '',
            icon: node.icon || '📚',
            category: category.id,
            difficulty: node.difficulty || 1,
            prerequisites: node.prerequisites || [],
            content: node.content || '',
          }));
          allTopics.push(...categoryTopics);
        }
      }

      // Store in Zustand
      setCategories(categories);
      setTopics(allTopics);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Show admin panel if enabled
  if (showAdmin) {
    return (
      <div className="app">
        <div
          style={{
            position: 'fixed',
            top: '1.25rem',
            right: '2rem',
            zIndex: 1000,
          }}
        >
          <button
            onClick={() => setShowAdmin(false)}
            className="btn-back-to-learning"
          >
            ← Back to Learning
          </button>
        </div>
        <AdminPanel />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="app">
        <div className="loading-screen">
          <div className="spinner"></div>
          <p>Loading your learning platform...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="app">
        <Header
          onShowSettings={() => setShowSettings(true)}
          onShowAdmin={() => setShowAdmin(true)}
        />

        <main className="main-content-new">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/category/:categoryId" element={<CategoryView />} />
            <Route
              path="/category/:categoryId/topic/:topicId"
              element={<CategoryView />}
            />
          </Routes>
        </main>

        {/* Modals */}
        <AnimatePresence>
          {showSettings && (
            <UserSettings userId={userId} onClose={() => setShowSettings(false)} />
          )}
        </AnimatePresence>
      </div>
    </Router>
  );
}

export default App;
