import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { BookOpen, Map, PanelLeftClose, PanelLeft } from 'lucide-react';
import Breadcrumbs from '../components/layout/Breadcrumbs';
import Sidebar from '../components/layout/Sidebar';
import StudyMode from '../components/study/StudyMode';
import ExploreMode from '../components/explore/ExploreMode';
import useAppStore from '../store/useAppStore';

const CategoryView = () => {
  const { categoryId, topicId } = useParams();
  const {
    categories,
    topics,
    viewMode,
    setViewMode,
    sidebarCollapsed,
    toggleSidebar,
  } = useAppStore();

  const category = categories.find((cat) => cat.id === categoryId);
  // Convert topicId to number for comparison (URL params are strings)
  const currentTopic = topicId ? topics.find((t) => t.id === parseInt(topicId, 10) || t.id === topicId) : null;

  if (!category) {
    return (
      <div className="error-page">
        <h2>Category not found</h2>
      </div>
    );
  }

  // Breadcrumbs
  const breadcrumbItems = [
    { label: category.name, path: `/category/${categoryId}` },
  ];

  if (currentTopic) {
    breadcrumbItems.push({ label: currentTopic.name, path: null });
  }

  const handleModeToggle = () => {
    setViewMode(viewMode === 'study' ? 'explore' : 'study');
  };

  return (
    <div className="category-view">
      {/* Top Bar */}
      <div className="category-view-header">
        <div className="category-view-header-left">
          <Breadcrumbs items={breadcrumbItems} />
        </div>

        <div className="category-view-header-right">
          {/* Sidebar Toggle */}
          {viewMode === 'study' && (
            <motion.button
              className="btn-icon"
              onClick={toggleSidebar}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title={sidebarCollapsed ? 'Show sidebar' : 'Hide sidebar'}
            >
              {sidebarCollapsed ? <PanelLeft size={20} /> : <PanelLeftClose size={20} />}
            </motion.button>
          )}

          {/* Mode Toggle */}
          <motion.button
            className={`btn-mode-toggle ${viewMode === 'explore' ? 'active' : ''}`}
            onClick={handleModeToggle}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {viewMode === 'study' ? (
              <>
                <Map size={18} />
                <span>Explore Mode</span>
              </>
            ) : (
              <>
                <BookOpen size={18} />
                <span>Study Mode</span>
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* Main Content */}
      <div className="category-view-content">
        <AnimatePresence mode="wait">
          {viewMode === 'study' ? (
            <motion.div
              key="study"
              className="study-layout"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              {!sidebarCollapsed && <Sidebar categoryId={categoryId} />}

              <div className="study-main">
                {currentTopic ? (
                  <StudyMode topic={currentTopic} categoryId={categoryId} />
                ) : (
                  <div className="study-placeholder">
                    <div className="placeholder-content">
                      <BookOpen size={48} strokeWidth={1.5} />
                      <h2>Select a topic to begin</h2>
                      <p>Choose a topic from the sidebar to start learning</p>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="explore"
              className="explore-layout"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <ExploreMode categoryId={categoryId} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default CategoryView;
