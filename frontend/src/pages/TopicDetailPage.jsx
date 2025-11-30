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

  // Get real topic data from navigation state (includes learning_structure from backend)
  const backendTopicData = location.state?.topicData;

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

  // Use real backend data if available, otherwise use placeholder
  const topicData = React.useMemo(() => {
    if (backendTopicData && backendTopicData.learning_structure) {
      // We have real data from backend!
      const structure = backendTopicData.learning_structure;

      return {
        name: topicName,
        priority: backendTopicData.priority || 'MEDIUM',
        coverage: backendTopicData.confidence ? (backendTopicData.confidence * 100).toFixed(1) : 0,
        booksCount: backendTopicData.all_sources?.length || 0,
        chunksCount: backendTopicData.all_sources?.reduce((sum, s) => sum + (s.chunks?.length || 0), 0) || 0,
        userProgress: 0, // TODO: Fetch from backend user progress API
        estimatedWeeks: Math.ceil(structure.estimated_hours / 10) || '3-4', // Assume 10 hours/week
        estimatedHours: structure.estimated_hours,
        difficultyLevel: structure.difficulty_level,
        cached: structure.cached,
        interviewFrequency: 80, // Placeholder - could be derived from priority
        prerequisiteFor: [], // TODO: Extract from dependencies

        whyMatters: `This topic appears in quant interviews for roles requiring ${backendTopicData.keywords?.slice(0, 3).join(', ')}. Master this to demonstrate your expertise in ${topicName}.`,

        interviewQuestions: [
          `Explain the key concepts in ${topicName}`,
          `How would you apply ${topicName} in trading strategies?`,
          `Walk through a practical example using ${topicName}`
        ],

        // Use real weeks/sections from backend!
        weeks: structure.weeks || [],

        // Map backend source books to display format
        books: backendTopicData.all_sources?.map(source => ({
          title: source.source || 'Book',
          sections: 'Multiple sections',
          chunks: source.chunks?.length || 0,
          topics: source.chunks?.slice(0, 3).map(c => c.text?.substring(0, 50)).join(', ') || topicName
        })) || [],

        practiceProblems: {
          easy: [
            { id: 1, text: `What are the key concepts in ${topicName}?`, completed: false },
            { id: 2, text: `When would you use ${topicName} in trading?`, completed: false },
            { id: 3, text: `What are the main assumptions or limitations?`, completed: false }
          ],
          medium: [
            { id: 4, text: `Derive or prove a key theorem in ${topicName}`, completed: false },
            { id: 5, text: `Solve a moderately complex problem using ${topicName}`, completed: false }
          ],
          hard: [
            { id: 6, text: `Implement ${topicName} from scratch (30 min)`, completed: false },
            { id: 7, text: `Apply ${topicName} to a real trading scenario`, completed: false }
          ]
        }
      };
    }

    // Fallback to placeholder data if no backend data available
    return {
      name: topicName,
      priority: 'MEDIUM',
      coverage: 54.9,
      booksCount: 3,
      chunksCount: 10,
      userProgress: 0,
      estimatedWeeks: '3-4',
      interviewFrequency: 90,
      prerequisiteFor: ['time series analysis', 'machine learning'],

      whyMatters: `Learn ${topicName} to excel in quant interviews. This topic is essential for understanding advanced concepts and solving real-world problems.`,

      interviewQuestions: [
        `Explain ${topicName} in your own words`,
        `How is ${topicName} applied in quantitative finance?`,
        `What are the key challenges when working with ${topicName}?`
      ],

      weeks: [
        {
          weekNumber: 1,
          title: 'Foundations',
          sections: [
            { id: '1.1', title: `Introduction to ${topicName}`, topics: ['Core concepts', 'Fundamentals'], resources: ['Reading materials'] }
          ]
        }
      ],

      books: [
        { title: 'Reference materials', sections: 'Various', chunks: 10, topics: topicName }
      ],

      practiceProblems: {
        easy: [
          { id: 1, text: `What are the basics of ${topicName}?`, completed: false }
        ],
        medium: [
          { id: 2, text: `Solve a problem using ${topicName}`, completed: false }
        ],
        hard: [
          { id: 3, text: `Implement ${topicName} from scratch`, completed: false }
        ]
      }
    };
  }, [backendTopicData, topicName]);

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

  // Calculate week progress based on completed sections
  const calculateWeekProgress = (week) => {
    if (!week.sections || week.sections.length === 0) return 0;

    const completedCount = week.sections.filter(
      section => sectionCompletionStatus[section.id] === true
    ).length;

    return Math.round((completedCount / week.sections.length) * 100);
  };

  // Check if entire week is completed
  const isWeekCompleted = (week) => {
    if (!week.sections || week.sections.length === 0) return false;
    return week.sections.every(section => sectionCompletionStatus[section.id] === true);
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

            {topicData.weeks.map((week) => {
              const weekProgress = calculateWeekProgress(week);
              const weekCompleted = isWeekCompleted(week);

              return (
              <div key={week.weekNumber} className="week-card">
                <div className="week-header">
                  <h3>Week {week.weekNumber}: {week.title}</h3>
                  <span className="week-status">
                    {weekCompleted ? '✅ Complete' : `${weekProgress}% complete`}
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
                            {
                              state: {
                                topicName: topicData.name,
                                sectionData: {
                                  title: section.title,
                                  topics: section.topics || [],
                                  weekNumber: week.weekNumber
                                }
                              }
                            }
                          );
                        }}
                      >
                        {section.completed ? 'Review' : 'Start Learning'} →
                      </button>
                    </div>
                  ))}
                </div>
              </div>
              );
            })}

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
