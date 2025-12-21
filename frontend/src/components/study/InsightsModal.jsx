import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Lightbulb, AlertTriangle, CheckCircle, GitCompare, Settings } from 'lucide-react';
import api from '../../services/api';

const InsightsModal = ({ isOpen, onClose, topicId, topicName }) => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && topicId) {
      fetchInsights();
    }
  }, [isOpen, topicId]);

  const fetchInsights = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get(`/api/insights/${topicId}`);
      setInsights(response.data);
    } catch (err) {
      console.error('Failed to fetch insights:', err);
      if (err.response?.status === 404) {
        setError('Insights not available for this topic yet.');
      } else {
        setError('Failed to load insights. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="insights-modal-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="insights-modal"
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="insights-modal-header">
            <div className="insights-modal-title">
              <Lightbulb size={24} className="insights-icon" />
              <div>
                <h2>Practitioner Insights</h2>
                <p className="insights-subtitle">{topicName}</p>
              </div>
            </div>
            <button className="insights-modal-close" onClick={onClose}>
              <X size={24} />
            </button>
          </div>

          {/* Content */}
          <div className="insights-modal-content">
            {loading && (
              <div className="insights-loading">
                <div className="spinner"></div>
                <p>Loading insights...</p>
              </div>
            )}

            {error && (
              <div className="insights-error">
                <AlertTriangle size={48} />
                <p>{error}</p>
              </div>
            )}

            {insights && !loading && !error && (
              <div className="insights-sections">
                {/* When to Use */}
                {insights.when_to_use && insights.when_to_use.length > 0 && (
                  <div className="insight-section">
                    <div className="insight-section-header">
                      <CheckCircle size={20} className="section-icon" />
                      <h3>When to Use</h3>
                    </div>
                    <div className="insight-items">
                      {insights.when_to_use.map((item, idx) => (
                        <div key={idx} className="insight-card">
                          <div className="insight-card-title">{item.scenario}</div>
                          <div className="insight-card-text">{item.rationale}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Limitations */}
                {insights.limitations && insights.limitations.length > 0 && (
                  <div className="insight-section">
                    <div className="insight-section-header">
                      <AlertTriangle size={20} className="section-icon warning" />
                      <h3>Limitations & Caveats</h3>
                    </div>
                    <div className="insight-items">
                      {insights.limitations.map((item, idx) => (
                        <div key={idx} className="insight-card warning">
                          <div className="insight-card-title">{item.issue}</div>
                          <div className="insight-card-text">{item.explanation}</div>
                          {item.mitigation && (
                            <div className="insight-mitigation">
                              → Mitigation: {item.mitigation}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Method Comparisons */}
                {insights.method_comparisons && insights.method_comparisons.length > 0 && (
                  <div className="insight-section">
                    <div className="insight-section-header">
                      <GitCompare size={20} className="section-icon" />
                      <h3>Comparison with Alternatives</h3>
                    </div>
                    <div className="insight-items">
                      {insights.method_comparisons.map((item, idx) => (
                        <div key={idx} className="insight-card comparison">
                          <div className="comparison-header">
                            <strong>{item.method_a}</strong> vs <strong>{item.method_b}</strong>
                          </div>
                          <div className="insight-card-text">
                            <strong>Key Difference:</strong> {item.key_difference}
                          </div>
                          <div className="insight-card-text">
                            <strong>When to Prefer:</strong> {item.when_to_prefer}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Practical Tips */}
                {insights.practical_tips && insights.practical_tips.length > 0 && (
                  <div className="insight-section">
                    <div className="insight-section-header">
                      <Settings size={20} className="section-icon" />
                      <h3>Practical Tips</h3>
                    </div>
                    <ul className="insight-list">
                      {insights.practical_tips.map((tip, idx) => (
                        <li key={idx}>{tip}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Computational Notes */}
                {insights.computational_notes && (
                  <div className="insight-section">
                    <div className="insight-section-header">
                      <Settings size={20} className="section-icon" />
                      <h3>Computational Considerations</h3>
                    </div>
                    <div className="insight-text">
                      {insights.computational_notes}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default InsightsModal;
