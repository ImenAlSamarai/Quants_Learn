import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import '../styles/TopicDetail.css';

/**
 * TopicDetailPage - Detailed view of a single topic with learning roadmap
 *
 * PLACEHOLDER VERSION - For testing user journey
 * TODO: Wire up with real backend data
 */
const TopicDetailPage = () => {
  const { topicSlug } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const topicName = location.state?.topicName || topicSlug.replace(/-/g, ' ');

  const [activeTab, setActiveTab] = useState('roadmap'); // roadmap, practice, progress
  const [sectionCompletionStatus, setSectionCompletionStatus] = useState({});

  // Load section completion status from localStorage
  useEffect(() => {
    const loadCompletionStatus = () => {
      const status = {};
      topicData.weeks.forEach(week => {
        week.sections.forEach(section => {
          const completionKey = `${topicSlug}-${week.weekNumber}-${section.id}-completed`;
          status[section.id] = localStorage.getItem(completionKey) === 'true';
        });
      });
      setSectionCompletionStatus(status);
    };

    loadCompletionStatus();

    // Listen for storage events to update when completion changes in other tabs
    const handleStorageChange = () => {
      loadCompletionStatus();
    };

    window.addEventListener('storage', handleStorageChange);
    // Also check periodically (in case completion happens in same tab)
    const interval = setInterval(loadCompletionStatus, 1000);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [topicSlug]);

  // PLACEHOLDER DATA - Replace with real API calls
  const topicData = {
    name: topicName,
    priority: 'MEDIUM',
    coverage: 54.9,
    booksCount: 3,
    chunksCount: 10,
    userProgress: 0,
    estimatedWeeks: '3-4',
    interviewFrequency: 90,
    prerequisiteFor: ['time series analysis', 'machine learning'],

    whyMatters: "Statistical modeling appears in 90% of quant interviews. You'll be asked to derive regression coefficients from first principles, explain bias-variance tradeoff, debug overfitting in production models, code linear regression from scratch (no sklearn), and discuss when to use Ridge vs Lasso.",

    interviewQuestions: [
      "Walk me through ordinary least squares derivation",
      "How would you detect heteroskedasticity?",
      "Implement gradient descent for linear regression in Python"
    ],

    weeks: [
      {
        weekNumber: 1,
        title: 'Foundations',
        completed: false,
        progress: 0,
        sections: [
          {
            id: '1.1',
            title: 'Linear Regression (OLS)',
            completed: false,
            topics: ['Matrix formulation: β = (X\'X)⁻¹X\'y', 'Assumptions (LINE)', 'Interpretation'],
            resources: ['ESL Chapter 3, sections 3.1-3.2', 'Quant Stats: Linear Models']
          },
          {
            id: '1.2',
            title: 'Maximum Likelihood Estimation',
            completed: false,
            topics: ['MLE framework', 'Connection to OLS'],
            resources: ['ESL Chapter 4, section 4.1']
          }
        ]
      },
      {
        weekNumber: 2,
        title: 'Model Diagnostics',
        completed: false,
        progress: 0,
        sections: [
          { id: '2.1', title: 'Residual Analysis', completed: false },
          { id: '2.2', title: 'Hypothesis Testing (t-tests, F-tests)', completed: false },
          { id: '2.3', title: 'Model Assumptions Validation', completed: false }
        ]
      },
      {
        weekNumber: 3,
        title: 'Advanced Topics',
        completed: false,
        progress: 0,
        sections: [
          { id: '3.1', title: 'Regularization (Ridge, Lasso, Elastic Net)', completed: false },
          { id: '3.2', title: 'Bias-Variance Tradeoff', completed: false },
          { id: '3.3', title: 'Cross-Validation', completed: false }
        ]
      },
      {
        weekNumber: 4,
        title: 'Interview Prep',
        completed: false,
        progress: 0,
        sections: [
          { id: '4.1', title: 'Coding from scratch (no libraries)', completed: false },
          { id: '4.2', title: 'Derivations & Proofs', completed: false },
          { id: '4.3', title: 'Mock interviews', completed: false }
        ]
      }
    ],

    books: [
      {
        title: 'Elements of Statistical Learning, Chapter 3',
        sections: '3.1, 3.2, 3.4',
        chunks: 7,
        topics: 'Linear Regression Fundamentals'
      },
      {
        title: 'Quant Learning Materials: Statistics',
        sections: 'Linear Models section',
        chunks: 3,
        topics: 'Linear Regression Fundamentals'
      },
      {
        title: 'Elements of Statistical Learning, Chapter 4',
        sections: '4.1-4.4',
        chunks: 2,
        topics: 'Generalized Linear Models'
      }
    ],

    practiceProblems: {
      easy: [
        { id: 1, text: 'Explain the difference between R² and adjusted R²', completed: false },
        { id: 2, text: 'When would you use Ridge vs Lasso regression?', completed: false },
        { id: 3, text: 'What are the OLS assumptions and why do they matter?', completed: false }
      ],
      medium: [
        { id: 4, text: 'Derive the closed-form solution for linear regression', completed: false },
        { id: 5, text: 'Prove that Ridge regression shrinks coefficients', completed: false },
        { id: 6, text: 'Show that R² always increases with more features', completed: false }
      ],
      hard: [
        { id: 7, text: 'Implement linear regression from scratch (30 min)', completed: false },
        { id: 8, text: 'Code Ridge regression with cross-validation', completed: false },
        { id: 9, text: 'Detect and fix multicollinearity in a dataset', completed: false }
      ]
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'HIGH': return '#EF4444';
      case 'MEDIUM': return '#F59E0B';
      case 'LOW': return '#10B981';
      default: return '#6B7280';
    }
  };

  const getProgressBar = (percent) => {
    const filled = Math.round(percent / 20);
    return '⚪'.repeat(5).split('').map((_, i) => i < filled ? '🟢' : '⚪').join('');
  };

  return (
    <div className="topic-detail-page">
      {/* Header with Back Button */}
      <header className="topic-header">
        <button onClick={() => navigate('/learning-path')} className="back-button">
          ← Back to Learning Path
        </button>
      </header>

      {/* Hero Section */}
      <section className="topic-hero">
        <div className="topic-title-section">
          <h1>📊 {topicData.name}</h1>
          <div className="topic-meta">
            <span className="priority-badge" style={{ borderColor: getPriorityColor(topicData.priority), color: getPriorityColor(topicData.priority) }}>
              Priority: {topicData.priority}
            </span>
            <span className="prerequisite-info">
              Prerequisite for {topicData.prerequisiteFor.length} topics
            </span>
          </div>
        </div>

        <div className="topic-stats-grid">
          <div className="stat-card">
            <div className="stat-label">Coverage</div>
            <div className="stat-value">✅ {topicData.coverage}%</div>
            <div className="stat-detail">{topicData.booksCount} books, {topicData.chunksCount} chunks</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Your Progress</div>
            <div className="stat-value">{getProgressBar(topicData.userProgress)}</div>
            <div className="stat-detail">{topicData.userProgress}% Complete</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Estimated Time</div>
            <div className="stat-value">{topicData.estimatedWeeks} weeks</div>
            <div className="stat-detail">To interview readiness</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Interview Frequency</div>
            <div className="stat-value">{topicData.interviewFrequency}%</div>
            <div className="stat-detail">Very High</div>
          </div>
        </div>
      </section>

      {/* Why This Matters */}
      <section className="why-matters-section">
        <h2>💼 Why This Matters (Interview Context)</h2>
        <p className="why-matters-text">{topicData.whyMatters}</p>

        <div className="interview-questions-preview">
          <h3>🎯 Real Interview Questions:</h3>
          <ol>
            {topicData.interviewQuestions.map((q, i) => (
              <li key={i}>"{q}"</li>
            ))}
          </ol>
        </div>
      </section>

      {/* Tab Navigation */}
      <nav className="topic-tabs">
        <button
          className={`tab ${activeTab === 'roadmap' ? 'active' : ''}`}
          onClick={() => setActiveTab('roadmap')}
        >
          📚 Learning Roadmap
        </button>
        <button
          className={`tab ${activeTab === 'practice' ? 'active' : ''}`}
          onClick={() => setActiveTab('practice')}
        >
          🎯 Practice Problems
        </button>
        <button
          className={`tab ${activeTab === 'progress' ? 'active' : ''}`}
          onClick={() => setActiveTab('progress')}
        >
          📊 Your Progress
        </button>
      </nav>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'roadmap' && (
          <section className="roadmap-section">
            <h2>📚 Mastery Path ({topicData.estimatedWeeks} weeks)</h2>

            {topicData.weeks.map((week) => (
              <div key={week.weekNumber} className="week-card">
                <div className="week-header">
                  <h3>Week {week.weekNumber}: {week.title}</h3>
                  <span className="week-status">
                    {week.completed ? '✅ Complete' : `${week.progress}% complete`}
                  </span>
                </div>

                <div className="sections-list">
                  {week.sections.map((section) => (
                    <div key={section.id} className="section-item">
                      <div className="section-header">
                        <input
                          type="checkbox"
                          checked={sectionCompletionStatus[section.id] || false}
                          readOnly
                          style={{ cursor: 'default' }}
                        />
                        <span className="section-id">{section.id}</span>
                        <span className="section-title">{section.title}</span>
                        {sectionCompletionStatus[section.id] && (
                          <span className="section-completed-badge">✓</span>
                        )}
                      </div>

                      {section.topics && (
                        <ul className="section-topics">
                          {section.topics.map((topic, i) => (
                            <li key={i}>{topic}</li>
                          ))}
                        </ul>
                      )}

                      {section.resources && (
                        <div className="section-resources">
                          📖 {section.resources.join(' | ')}
                        </div>
                      )}

                      <button
                        className="start-section-btn"
                        onClick={() => {
                          navigate(
                            `/topic/${topicSlug}/week/${week.weekNumber}/section/${section.id}`,
                            { state: { topicName: topicData.name } }
                          );
                        }}
                      >
                        {section.completed ? 'Review' : 'Start Learning'} →
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Available Books */}
            <div className="books-section">
              <h3>📖 Available Resources</h3>
              {topicData.books.map((book, i) => (
                <div key={i} className="book-card">
                  <div className="book-info">
                    <h4>{book.title}</h4>
                    <p>Sections: {book.sections} | {book.chunks} chunks indexed</p>
                    <p className="book-topic">{book.topics}</p>
                  </div>
                  <div className="book-actions">
                    <button className="btn-secondary">View Chapter</button>
                    <button className="btn-secondary">Download PDF</button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {activeTab === 'practice' && (
          <section className="practice-section">
            <h2>🎯 Practice Problems</h2>

            <div className="difficulty-section">
              <h3>Easy (Conceptual Understanding)</h3>
              {topicData.practiceProblems.easy.map((problem) => (
                <div key={problem.id} className="practice-item">
                  <input type="checkbox" checked={problem.completed} onChange={() => {}} />
                  <span>Q{problem.id}: {problem.text}</span>
                  <button className="btn-practice">Answer</button>
                </div>
              ))}
            </div>

            <div className="difficulty-section">
              <h3>Medium (Mathematical Derivations)</h3>
              {topicData.practiceProblems.medium.map((problem) => (
                <div key={problem.id} className="practice-item">
                  <input type="checkbox" checked={problem.completed} onChange={() => {}} />
                  <span>Q{problem.id}: {problem.text}</span>
                  <button className="btn-practice">Start</button>
                </div>
              ))}
            </div>

            <div className="difficulty-section">
              <h3>Hard (Coding Challenges)</h3>
              {topicData.practiceProblems.hard.map((problem) => (
                <div key={problem.id} className="practice-item">
                  <input type="checkbox" checked={problem.completed} onChange={() => {}} />
                  <span>Q{problem.id}: {problem.text}</span>
                  <button className="btn-practice">Code</button>
                </div>
              ))}
            </div>

            <div className="mock-interview-card">
              <h3>🎬 Interview Simulation</h3>
              <p>45-minute mock interview with live coding + whiteboard + conceptual questions</p>
              <button className="btn-primary">Start Mock Interview</button>
            </div>
          </section>
        )}

        {activeTab === 'progress' && (
          <section className="progress-section">
            <h2>📊 Your Progress</h2>

            <div className="progress-overview">
              <div className="progress-metric">
                <h3>Reading Completed</h3>
                <div className="checklist">
                  <div>□ ESL Chapter 3.1-3.2 (Linear Regression)</div>
                  <div>□ ESL Chapter 3.4 (Regularization)</div>
                  <div>□ Quant Stats: Linear Models</div>
                </div>
              </div>

              <div className="progress-metric">
                <h3>Concepts Mastered</h3>
                <div className="concept-status">
                  <div>✅ 8/15 concepts understood</div>
                  <div>□ Bias-variance tradeoff</div>
                  <div>□ Regularization theory</div>
                  <div>⚠️ Need review: Maximum Likelihood</div>
                </div>
              </div>

              <div className="progress-metric">
                <h3>Practice Problems</h3>
                <div className="practice-stats">
                  <div>3/12 completed (25%)</div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{width: '25%'}}></div>
                  </div>
                </div>
              </div>

              <div className="readiness-card">
                <h3>Interview Readiness</h3>
                <div className="readiness-score">35% 🟡</div>
                <p>Recommendation: Complete Week 2 material before interviews</p>
              </div>
            </div>
          </section>
        )}
      </div>

      {/* Action Buttons */}
      <div className="action-footer">
        <button className="btn-secondary" onClick={() => navigate('/learning-path')}>
          Back to Learning Path
        </button>
        <button
          className="btn-primary"
          onClick={() => {
            // Navigate to first section of first week
            const firstWeek = topicData.weeks[0];
            const firstSection = firstWeek.sections[0];
            navigate(
              `/topic/${topicSlug}/week/${firstWeek.weekNumber}/section/${firstSection.id}`,
              { state: { topicName: topicData.name } }
            );
          }}
        >
          Start Learning →
        </button>
      </div>
    </div>
  );
};

export default TopicDetailPage;
