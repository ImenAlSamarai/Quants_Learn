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
  // Make content dynamic based on sectionId
  const getSectionData = () => {
    const baseData = {
      topicName: location.state?.topicName || topicSlug.replace(/-/g, ' '),
      weekNumber: parseInt(weekNumber) || 1,
      sectionId: sectionId || '1.1',
    };

    // Define content for each section (placeholder)
    const sectionContent = {
      '1.1': {
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
            }
          ],
          keyTakeaways: [
            'β̂ = (XᵀX)⁻¹Xᵀy is THE formula you must know',
            'OLS minimizes sum of squared residuals',
            'LINE assumptions required for BLUE property'
          ],
          interviewTips: [
            'Be ready to derive β̂ on a whiteboard in under 5 minutes',
            'Know the difference between unbiased and BLUE'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Easy', text: 'Show that the OLS estimator is unbiased: E[β̂] = β' },
            { id: 2, difficulty: 'Medium', text: 'Derive the variance of β̂: Var(β̂) = σ²(XᵀX)⁻¹' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 3, Section 3.2', pages: 'pp. 43-55' }
          ]
        }
      },
      '1.2': {
        sectionTitle: 'Maximum Likelihood Estimation',
        estimatedTime: '40 minutes',
        content: {
          introduction: "Maximum Likelihood Estimation (MLE) is a fundamental method for parameter estimation in statistics. Understanding the connection between MLE and OLS is crucial for interviews.",
          sections: [
            {
              title: 'The MLE Framework',
              content: `The likelihood function measures how likely the observed data is for different parameter values.

Given data x₁, x₂, ..., xₙ and parameter θ:

L(θ | x) = P(x | θ) = ∏ᵢ P(xᵢ | θ)

The MLE finds the parameter that maximizes this likelihood:

θ̂ₘₗₑ = argmax L(θ | x)

In practice, we maximize the log-likelihood:
ℓ(θ) = log L(θ) = ∑ᵢ log P(xᵢ | θ)`,
              keyFormula: 'θ̂ₘₗₑ = argmax ∑ᵢ log P(xᵢ | θ)'
            },
            {
              title: 'Connection to OLS',
              content: `Under the assumption that errors are normally distributed:
εᵢ ~ N(0, σ²)

The likelihood of the data is:
L(β, σ² | y, X) = ∏ᵢ (1/√(2πσ²)) exp(-(yᵢ - xᵢᵀβ)²/(2σ²))

Taking the log and maximizing with respect to β gives:
β̂ₘₗₑ = (XᵀX)⁻¹Xᵀy

This is exactly the OLS estimator! MLE and OLS coincide under normality.`
            }
          ],
          keyTakeaways: [
            'MLE maximizes the likelihood of observed data',
            'Log-likelihood is easier to work with than likelihood',
            'Under normality, MLE = OLS for linear regression',
            'MLE is consistent and asymptotically normal'
          ],
          interviewTips: [
            'Know how to derive MLE for simple distributions (Normal, Bernoulli)',
            'Understand when MLE and OLS give the same answer',
            'Be ready to explain asymptotic properties'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Easy', text: 'Find the MLE for μ and σ² for Normal(μ, σ²)' },
            { id: 2, difficulty: 'Medium', text: 'Show that OLS = MLE under Gaussian errors' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 4, Section 4.1', pages: 'pp. 101-110' }
          ]
        }
      },
      // Add more sections as needed
      '2.1': {
        sectionTitle: 'Residual Analysis',
        estimatedTime: '35 minutes',
        content: {
          introduction: "After fitting a regression model, analyzing residuals is crucial for validating model assumptions and detecting problems.",
          sections: [
            { title: 'What are Residuals?', content: 'Residuals are the differences between observed and predicted values...' }
          ],
          keyTakeaways: ['Residual plots reveal model violations', 'QQ plots check normality'],
          interviewTips: ['Be able to interpret residual plots'],
          practiceProblems: [{ id: 1, difficulty: 'Easy', text: 'Identify heteroskedasticity from a residual plot' }],
          resources: [{ source: 'Quant Stats', chapter: 'Regression Diagnostics', pages: 'Full section' }]
        }
      }
    };

    const content = sectionContent[sectionId] || sectionContent['1.1'];

    // Navigation logic
    const allSections = [
      { id: '1.1', title: 'Linear Regression (OLS)' },
      { id: '1.2', title: 'Maximum Likelihood Estimation' },
      { id: '2.1', title: 'Residual Analysis' },
      { id: '2.2', title: 'Hypothesis Testing' }
    ];

    const currentIndex = allSections.findIndex(s => s.id === sectionId);
    const previous = currentIndex > 0 ? allSections[currentIndex - 1] : null;
    const next = currentIndex < allSections.length - 1 ? allSections[currentIndex + 1] : null;

    return {
      ...baseData,
      ...content,
      navigation: {
        previous,
        next,
        allSections: allSections.map(s => ({ ...s, current: s.id === sectionId }))
      }
    };
  };

  const sectionData = getSectionData();

  const handleComplete = () => {
    setCompleted(true);
    alert('Section marked as complete! Progress saved.');
  };

  const handleNext = () => {
    if (sectionData.navigation.next) {
      navigate(`/topic/${topicSlug}/week/${weekNumber}/section/${sectionData.navigation.next.id}`, {
        state: { topicName: sectionData.topicName }
      });
    }
  };

  const handlePrevious = () => {
    if (sectionData.navigation.previous) {
      navigate(`/topic/${topicSlug}/week/${weekNumber}/section/${sectionData.navigation.previous.id}`, {
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
              <button onClick={handlePrevious} className="nav-btn prev">
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
