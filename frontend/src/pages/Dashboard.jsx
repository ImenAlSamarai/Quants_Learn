import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUser } from '../services/auth';
import { getLearningPath, fetchUserProgress } from '../services/api';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [learningPath, setLearningPath] = useState(null);
  const [userProgress, setUserProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUpdateWarning, setShowUpdateWarning] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);


  const loadDashboardData = async () => {
    try {
      const currentUser = getUser();
      if (!currentUser) {
        navigate('/login');
        return;
      }

      setUser(currentUser);

      // Fetch user's learning path and progress
      try {
        const path = await getLearningPath(currentUser.user_id);
        setLearningPath(path);

        // Fetch user progress data
        const progressData = await fetchUserProgress(currentUser.user_id);
        // Extract the progress array from the response object
        const progressArray = progressData?.progress || [];
        setUserProgress(progressArray);
      } catch (error) {
        // No learning path yet - this is okay for new users
        console.log('No learning path found:', error);
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAllTopics = () => {
    if (!learningPath || !learningPath.stages) return [];

    const topics = [];
    try {
      learningPath.stages.forEach(stage => {
        if (stage.topics && Array.isArray(stage.topics)) {
          stage.topics.forEach(topic => {
            // Handle different topic formats
            const topicName = typeof topic === 'string'
              ? topic
              : (topic.name || topic.topic || 'Unknown Topic');

            topics.push({
              name: topicName,
              stage: stage.stage_name || 'General',
              priority: typeof topic === 'object' ? (topic.priority || 'MEDIUM') : 'MEDIUM'
            });
          });
        }
      });
    } catch (error) {
      console.error('Error parsing topics:', error);
    }
    return topics;
  };

  // Get topic progress from localStorage (where section completion is actually stored)
  const getTopicProgressFromLocalStorage = (topicName) => {
    try {
      const topicSlug = topicName.toLowerCase().replace(/\s+/g, '-');
      let completedSections = 0;
      let totalSections = 0;

      // The learning_structure is stored in covered_topics, NOT in stages.topics
      // We need to find the topic in covered_topics array
      if (learningPath && learningPath.covered_topics && Array.isArray(learningPath.covered_topics)) {
        const coveredTopic = learningPath.covered_topics.find(ct => {
          const ctName = ct.topic || ct.name;
          return ctName === topicName;
        });

        if (coveredTopic && coveredTopic.learning_structure && coveredTopic.learning_structure.weeks) {
          // Count sections in this topic
          coveredTopic.learning_structure.weeks.forEach(week => {
            if (week.sections && Array.isArray(week.sections)) {
              week.sections.forEach(section => {
                totalSections++;
                // Check localStorage for completion
                const completionKey = `${topicSlug}-${week.weekNumber}-${section.id}-completed`;
                if (localStorage.getItem(completionKey) === 'true') {
                  completedSections++;
                }
              });
            }
          });
        }
      }

      return { completedSections, totalSections };
    } catch (error) {
      console.error('Error checking topic progress from localStorage:', error);
      return { completedSections: 0, totalSections: 0 };
    }
  };

  const getTopicProgress = (topicName) => {
    const { completedSections, totalSections } = getTopicProgressFromLocalStorage(topicName);
    return totalSections > 0 ? Math.round((completedSections / totalSections) * 100) : 0;
  };

  const calculateProgress = () => {
    const topics = getAllTopics();
    if (topics.length === 0) return 0;

    // Calculate average progress across all topics
    let totalSections = 0;
    let completedSections = 0;

    topics.forEach(topic => {
      const { completedSections: completed, totalSections: total } = getTopicProgressFromLocalStorage(topic.name);
      completedSections += completed;
      totalSections += total;
    });

    return totalSections > 0 ? Math.round((completedSections / totalSections) * 100) : 0;
  };

  const formatJobTitle = () => {
    if (!learningPath) return 'Your Learning Path';

    // Try to extract job title from role_type
    if (learningPath.role_type) {
      return learningPath.role_type
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    }

    return 'Your Learning Path';
  };

  const handleUpdateJob = () => {
    if (learningPath) {
      // Show warning if user has existing path
      setShowUpdateWarning(true);
    } else {
      // No existing path, go straight to job input
      navigate('/create-path');
    }
  };

  const confirmUpdateJob = () => {
    setShowUpdateWarning(false);
    navigate('/create-path');
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.name || user?.user_id}!</h1>
        <p className="dashboard-subtitle">Track your learning progress and continue your journey</p>
      </div>

      {learningPath ? (
        <div className="dashboard-content">
          <div className="learning-path-card">
            <div className="card-header">
              <h2>Your Learning Path</h2>
              <span className="coverage-badge">
                {learningPath.coverage_percentage}% Coverage
              </span>
            </div>

            <div className="job-info">
              <h3>{formatJobTitle()}</h3>
              <p className="job-description-preview">
                Based on your target job requirements
              </p>
            </div>

            <div className="progress-section">
              <div className="progress-label">
                <span>Overall Progress</span>
                <span>{calculateProgress()}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${calculateProgress()}%` }}
                ></div>
              </div>
            </div>

            {/* Topic Progress List */}
            {getAllTopics().length > 0 && (
              <div className="topics-progress-section">
                <h3 className="section-heading">Required Topics</h3>
                <div className="topics-list">
                  {getAllTopics().map((topic, index) => {
                    const progressPercent = getTopicProgress(topic.name);
                    const isCompleted = progressPercent === 100;
                    const hasProgress = progressPercent > 0;
                    return (
                      <div key={index} className="topic-item">
                        <span className={`topic-status ${isCompleted ? 'completed' : 'pending'}`}>
                          {isCompleted ? '✓' : '○'}
                        </span>
                        <div className="topic-details">
                          <span className="topic-name">{topic.name}</span>
                          <span className="topic-stage">{topic.stage}</span>
                        </div>
                        <div className="topic-priority-slot">
                          {topic.priority === 'HIGH' && (
                            <span className="priority-badge">High Priority</span>
                          )}
                        </div>
                        <div className="topic-progress-bar">
                          <div className="topic-progress-bar-bg">
                            <div
                              className="topic-progress-bar-fill"
                              style={{ width: `${progressPercent}%` }}
                            ></div>
                          </div>
                          <span className="topic-progress-percent">{progressPercent}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            <div className="card-actions">
              <button
                className="btn-primary"
                onClick={() => navigate('/learning-path')}
              >
                Continue Learning →
              </button>
              <button
                className="btn-secondary"
                onClick={handleUpdateJob}
              >
                Update Job Target
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="dashboard-content">
          <div className="empty-state">
            <div className="empty-state-icon">📚</div>
            <h2>No Learning Path Yet</h2>
            <p>Create your first personalized learning path by entering a job description.</p>
            <button
              className="btn-primary"
              onClick={() => navigate('/create-path')}
            >
              Create Learning Path
            </button>
          </div>
        </div>
      )}

      {/* Role-specific info */}
      {user?.role === 'recruiter' && (
        <div className="recruiter-section">
          <h3>Recruiter Tools (Coming Soon)</h3>
          <p>Find and connect with qualified candidates based on their learning progress.</p>
        </div>
      )}

      {/* Update Job Warning Modal */}
      {showUpdateWarning && (
        <div className="modal-overlay" onClick={() => setShowUpdateWarning(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Update Job Target?</h3>
            <p>
              Creating a new learning path will replace your current path. Your progress on
              completed modules will be preserved, but the topic list will be updated based on
              the new job requirements.
            </p>
            <p className="warning-text">
              <strong>Note:</strong> Currently, you can only track one job at a time.
              Multi-job support coming soon!
            </p>
            <div className="modal-actions">
              <button
                className="btn-secondary"
                onClick={() => setShowUpdateWarning(false)}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={confirmUpdateJob}
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
