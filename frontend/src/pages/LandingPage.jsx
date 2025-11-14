import { motion } from 'framer-motion';
import { Brain, Sparkles } from 'lucide-react';
import CategoryCard from '../components/discovery/CategoryCard';
import ProgressStats from '../components/discovery/ProgressStats';
import RecommendedTopics from '../components/discovery/RecommendedTopics';
import useAppStore from '../store/useAppStore';

const LandingPage = () => {
  const categories = useAppStore((state) => state.categories);

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <motion.section
        className="hero-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="hero-content">
          <motion.div
            className="hero-icon"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          >
            <Brain size={48} strokeWidth={1.5} />
          </motion.div>
          <h1 className="hero-title">
            Master Quantitative Finance
          </h1>
          <p className="hero-subtitle">
            Explore interconnected topics, build deep understanding, and advance your quant skills
            through interactive learning paths
          </p>
          <motion.div
            className="hero-badge"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <Sparkles size={16} />
            <span>Interactive • Progressive • Comprehensive</span>
          </motion.div>
        </div>
      </motion.section>

      {/* Progress Stats */}
      <section className="stats-section">
        <ProgressStats />
      </section>

      {/* Recommended Topics */}
      <RecommendedTopics />

      {/* Categories Grid */}
      <section className="categories-section">
        <div className="section-header">
          <h2 className="section-title">Learning Paths</h2>
          <p className="section-subtitle">
            Choose a category to begin your journey
          </p>
        </div>

        <div className="categories-grid">
          {categories.map((category, index) => (
            <CategoryCard key={category.id} category={category} />
          ))}
        </div>
      </section>

      {/* Quick Tips */}
      <motion.section
        className="tips-section"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <div className="tips-content">
          <h3 className="tips-title">💡 Learning Tips</h3>
          <ul className="tips-list">
            <li>Start with fundamentals before advancing to complex topics</li>
            <li>Complete prerequisite topics to unlock new content</li>
            <li>Switch between Study and Explore modes to visualize connections</li>
            <li>Track your progress and maintain consistency</li>
          </ul>
        </div>
      </motion.section>
    </div>
  );
};

export default LandingPage;
