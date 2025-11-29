import React, { useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import '../styles/SectionContent.css';

/**
 * SectionContentPage - Display actual learning content for a section
 *
 * PLACEHOLDER VERSION - For testing user journey
 * TODO: Wire up with real book content from backend
 */
const SectionContentPage = () => {
  const { topicSlug, weekNumber, sectionId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [showNotes, setShowNotes] = useState(false);
  const [notes, setNotes] = useState('');
  const [completed, setCompleted] = useState(false);

  // PLACEHOLDER DATA - Replace with real API calls
  const sectionData = {
    topicName: location.state?.topicName || topicSlug.replace(/-/g, ' '),
    weekNumber: parseInt(weekNumber) || 1,
    sectionId: sectionId || '1.1',
    sectionTitle: 'Linear Regression (OLS)',
    estimatedTime: '45 minutes',

    content: {
      introduction: "Ordinary Least Squares (OLS) is the foundation of statistical modeling and one of the most commonly tested topics in quant interviews. You'll be expected to derive the OLS estimator, explain its assumptions, and implement it from scratch.",

      sections: [
        {
          title: 'The OLS Problem',
          content: `Given data points (x₁, y₁), (x₂, y₂), ..., (xₙ, yₙ), we want to find the line that best fits the data.

The linear model assumes:
y = Xβ + ε

where:
• y is the n×1 vector of responses
• X is the n×p design matrix
• β is the p×1 vector of coefficients
• ε is the n×1 vector of errors

The OLS estimator minimizes the sum of squared residuals:

minimize ||y - Xβ||²`
        },
        {
          title: 'Deriving the OLS Estimator',
          content: `To find the optimal β, we take the derivative and set it to zero:

∂/∂β ||y - Xβ||² = 0

Expanding:
(y - Xβ)ᵀ(y - Xβ) = yᵀy - 2βᵀXᵀy + βᵀXᵀXβ

Taking the derivative:
∂/∂β = -2Xᵀy + 2XᵀXβ = 0

Solving for β:
XᵀXβ = Xᵀy
β̂ = (XᵀX)⁻¹Xᵀy

This is the **OLS estimator** - you must memorize this formula!`,
          keyFormula: 'β̂ = (XᵀX)⁻¹Xᵀy'
        },
        {
          title: 'Assumptions (LINE)',
          content: `For OLS to be the Best Linear Unbiased Estimator (BLUE), we need:

**L**inearity: The relationship is linear in parameters
**I**ndependence: Observations are independent
**N**ormality: Errors are normally distributed
**E**qual variance: Homoskedasticity (constant error variance)

Interview Question: "What happens if assumptions are violated?"
• Linearity violated → Model is misspecified
• Independence violated → Standard errors are wrong
• Normality violated → Inference is invalid (large samples OK)
• Equal variance violated → OLS still unbiased but not efficient`
        },
        {
          title: 'Geometric Interpretation',
          content: `The OLS solution has a beautiful geometric interpretation:

ŷ = Xβ̂ = X(XᵀX)⁻¹Xᵀy

The matrix H = X(XᵀX)⁻¹Xᵀ is called the "hat matrix" because it puts the hat on y.

Key insight: H is a **projection matrix** that projects y onto the column space of X. The residual vector (y - ŷ) is orthogonal to the column space of X.

This means: Xᵀ(y - Xβ̂) = 0

This orthogonality condition is fundamental to understanding regression!`
        }
      ],

      keyTakeaways: [
        'β̂ = (XᵀX)⁻¹Xᵀy is THE formula you must know',
        'OLS minimizes sum of squared residuals',
        'LINE assumptions required for BLUE property',
        'Hat matrix H projects y onto column space of X',
        'Residuals are orthogonal to fitted values'
      ],

      interviewTips: [
        'Be ready to derive β̂ on a whiteboard in under 5 minutes',
        'Know the difference between unbiased and BLUE',
        'Understand when to use weighted least squares instead',
        'Be able to code OLS from scratch using numpy'
      ],

      practiceProblems: [
        {
          id: 1,
          difficulty: 'Easy',
          text: 'Show that the OLS estimator is unbiased: E[β̂] = β'
        },
        {
          id: 2,
          difficulty: 'Medium',
          text: 'Derive the variance of β̂: Var(β̂) = σ²(XᵀX)⁻¹'
        },
        {
          id: 3,
          difficulty: 'Hard',
          text: 'Implement OLS regression from scratch using only numpy'
        }
      ],

      resources: [
        {
          source: 'Elements of Statistical Learning',
          chapter: 'Chapter 3, Section 3.2',
          pages: 'pp. 43-55'
        },
        {
          source: 'Quant Learning Materials: Statistics',
          chapter: 'Linear Models',
          pages: 'Full section'
        }
      ]
    },

    navigation: {
      previous: null, // First section
      next: {
        sectionId: '1.2',
        title: 'Maximum Likelihood Estimation'
      },
      allSections: [
        { id: '1.1', title: 'Linear Regression (OLS)', current: true },
        { id: '1.2', title: 'Maximum Likelihood Estimation', current: false },
        { id: '2.1', title: 'Residual Analysis', current: false },
        { id: '2.2', title: 'Hypothesis Testing', current: false }
      ]
    }
  };

  const handleComplete = () => {
    setCompleted(true);
    alert('Section marked as complete! Progress saved.');
  };

  const handleNext = () => {
    if (sectionData.navigation.next) {
      navigate(`/topic/${topicSlug}/week/${weekNumber}/section/${sectionData.navigation.next.sectionId}`, {
        state: { topicName: sectionData.topicName }
      });
    }
  };

  return (
    <div className="section-content-page">
      {/* Header with Navigation */}
      <header className="section-header">
        <button
          onClick={() => navigate(`/topic/${topicSlug}`, { state: { topicName: sectionData.topicName } })}
          className="back-button"
        >
          ← Back to {sectionData.topicName}
        </button>

        <div className="section-meta">
          <span className="week-indicator">Week {sectionData.weekNumber}</span>
          <span className="section-indicator">Section {sectionData.sectionId}</span>
          <span className="time-estimate">⏱️ {sectionData.estimatedTime}</span>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="section-progress-bar">
        <div className="progress-track">
          {sectionData.navigation.allSections.map((section, index) => (
            <div
              key={section.id}
              className={`progress-node ${section.current ? 'current' : ''} ${index < sectionData.navigation.allSections.findIndex(s => s.current) ? 'completed' : ''}`}
              title={section.title}
            >
              {section.id}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main className="section-main">
        <div className="content-column">
          <h1>{sectionData.sectionTitle}</h1>

          {/* Introduction */}
          <div className="intro-box">
            <p>{sectionData.content.introduction}</p>
          </div>

          {/* Content Sections */}
          {sectionData.content.sections.map((section, index) => (
            <section key={index} className="content-section">
              <h2>{section.title}</h2>
              <div className="content-text">
                {section.content.split('\n').map((paragraph, i) => (
                  paragraph.trim() && <p key={i}>{paragraph}</p>
                ))}
              </div>
              {section.keyFormula && (
                <div className="formula-highlight">
                  <div className="formula-label">KEY FORMULA</div>
                  <div className="formula-text">{section.keyFormula}</div>
                </div>
              )}
            </section>
          ))}

          {/* Key Takeaways */}
          <div className="takeaways-box">
            <h3>🎯 Key Takeaways</h3>
            <ul>
              {sectionData.content.keyTakeaways.map((takeaway, i) => (
                <li key={i}>{takeaway}</li>
              ))}
            </ul>
          </div>

          {/* Interview Tips */}
          <div className="interview-tips-box">
            <h3>💼 Interview Tips</h3>
            <ul>
              {sectionData.content.interviewTips.map((tip, i) => (
                <li key={i}>{tip}</li>
              ))}
            </ul>
          </div>

          {/* Practice Problems */}
          <div className="practice-box">
            <h3>📝 Practice Problems</h3>
            {sectionData.content.practiceProblems.map((problem) => (
              <div key={problem.id} className="practice-item">
                <span className={`difficulty-badge ${problem.difficulty.toLowerCase()}`}>
                  {problem.difficulty}
                </span>
                <span className="problem-text">{problem.text}</span>
                <button className="btn-try">Try It</button>
              </div>
            ))}
          </div>

          {/* Resources */}
          <div className="resources-box">
            <h3>📚 Reading Material</h3>
            {sectionData.content.resources.map((resource, i) => (
              <div key={i} className="resource-item">
                <div className="resource-source">{resource.source}</div>
                <div className="resource-details">{resource.chapter} • {resource.pages}</div>
                <button className="btn-view">View PDF</button>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar */}
        <aside className="content-sidebar">
          {/* Completion Status */}
          <div className="completion-card">
            <h4>Section Progress</h4>
            {completed ? (
              <div className="completed-status">
                <span className="check-icon">✅</span>
                <span>Completed!</span>
              </div>
            ) : (
              <button onClick={handleComplete} className="btn-complete">
                Mark as Complete
              </button>
            )}
          </div>

          {/* Quick Notes */}
          <div className="notes-card">
            <div className="notes-header">
              <h4>Your Notes</h4>
              <button onClick={() => setShowNotes(!showNotes)} className="btn-toggle-notes">
                {showNotes ? '−' : '+'}
              </button>
            </div>
            {showNotes && (
              <textarea
                className="notes-textarea"
                placeholder="Write your notes here..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={10}
              />
            )}
          </div>

          {/* Navigation */}
          <div className="nav-card">
            <h4>Navigation</h4>
            {sectionData.navigation.previous && (
              <button className="nav-btn prev">
                ← Previous: {sectionData.navigation.previous.title}
              </button>
            )}
            {sectionData.navigation.next && (
              <button onClick={handleNext} className="nav-btn next">
                Next: {sectionData.navigation.next.title} →
              </button>
            )}
          </div>

          {/* Study Tips */}
          <div className="tips-card">
            <h4>💡 Study Tips</h4>
            <ul>
              <li>Work through derivations by hand</li>
              <li>Code the algorithm yourself</li>
              <li>Explain concepts out loud</li>
              <li>Practice on whiteboard</li>
            </ul>
          </div>
        </aside>
      </main>
    </div>
  );
};

export default SectionContentPage;
