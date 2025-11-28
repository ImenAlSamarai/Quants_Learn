import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import Home from './pages/Home';
import LandingPage from './pages/LandingPage';
import CategoryView from './pages/CategoryView';
import AdminPanel from './components/AdminPanel';
import LearningPathView from './components/LearningPathView';
import useAppStore from './store/useAppStore';
import { fetchMindMap } from './services/api';

function App() {
  const [loading, setLoading] = useState(true);
  const [userId] = useState('demo_user');
  const [showAdmin, setShowAdmin] = useState(false);

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
    {
      id: 'machine_learning',
      name: 'Machine Learning',
      icon: '🤖',
      description: 'Classical statistical learning (ESL) and modern deep learning (Bishop & Bishop). Covers regression, classification, tree methods, neural networks, CNNs, and transformers with book-grounded content',
      difficulty: 4,
    },
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    console.log('🚀 [App] Starting to load data...');
    setLoading(true);
    try {
      // Load all categories' data
      const allTopics = [];

      for (const category of categories) {
        console.log(`🔵 [App] Fetching data for category: ${category.id}`);
        const data = await fetchMindMap(category.id);

        console.log(`✅ [App] Received data for ${category.id}:`, {
          nodesCount: data.nodes?.length,
          edgesCount: data.edges?.length,
          firstNode: data.nodes?.[0],
        });

        // Transform nodes to topics
        if (data.nodes) {
          const categoryTopics = data.nodes.map((node) => ({
            id: node.id,
            name: node.title || node.name, // Fix: API returns 'title'
            description: node.description || '',
            icon: node.icon || '📚',
            category: category.id,
            difficulty: node.difficulty_level || node.difficulty || 1, // Fix: API returns 'difficulty_level'
            prerequisites: node.parent_ids || node.prerequisites || [], // Fix: API returns 'parent_ids'
            content: node.content || '',
            extra_metadata: node.extra_metadata || null, // Include learning path metadata
          }));

          console.log(`🔵 [App] Transformed ${categoryTopics.length} topics for ${category.id}:`, categoryTopics);
          allTopics.push(...categoryTopics);
        }
      }

      console.log('✅ [App] All topics loaded:', {
        totalTopics: allTopics.length,
        byCategory: allTopics.reduce((acc, topic) => {
          acc[topic.category] = (acc[topic.category] || 0) + 1;
          return acc;
        }, {}),
      });

      // Store in Zustand
      setCategories(categories);
      setTopics(allTopics);
    } catch (error) {
      console.error('❌ [App] Error loading data:', error);
    } finally {
      setLoading(false);
      console.log('🚀 [App] Data loading complete');
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
          onShowAdmin={() => setShowAdmin(true)}
        />

        <main className="main-content-new">
          <Routes>
            <Route path="/" element={<Home userId={userId} />} />
            <Route path="/explore" element={<LandingPage />} />
            <Route path="/category/:categoryId" element={<CategoryView />} />
            <Route
              path="/category/:categoryId/topic/:topicId"
              element={<CategoryView />}
            />
            <Route path="/learning-path" element={<LearningPathView userId={userId} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
