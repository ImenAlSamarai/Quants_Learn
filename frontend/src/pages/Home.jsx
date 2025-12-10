import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { updateJobProfile } from '../services/api';
import '../styles/Home.css';

const Home = ({ userId = 'demo_user' }) => {
  const navigate = useNavigate();

  const [userName, setUserName] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobSeniority, setJobSeniority] = useState('mid');
  const [firm, setFirm] = useState('');

  const [loading, setLoading] = useState(true);
  const [generatingPath, setGeneratingPath] = useState(false);
  const [learningPath, setLearningPath] = useState(null);

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/users/${encodeURIComponent(userId)}`);
      if (response.ok) {
        const data = await response.json();
        setUserName(data.name || '');
        setJobTitle(data.job_title || '');
        setJobDescription(data.job_description || '');
        setJobSeniority(data.job_seniority || 'mid');
        setFirm(data.firm || '');
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePath = async () => {
    if (!jobDescription || jobDescription.trim().length < 20) {
      alert('⚠️ Please provide a job description (at least 20 characters) to generate your personalized learning path.');
      return;
    }

    setGeneratingPath(true);
    setLearningPath(null);

    try {
      const result = await updateJobProfile(userId, {
        name: userName,
        job_title: jobTitle,
        job_description: jobDescription,
        job_seniority: jobSeniority,
        firm: firm || undefined,
      });

      setGeneratingPath(false);
      setLearningPath(result.learning_path);

      // Success notification
      alert(
        `✓ Job profile saved and learning path generated!\n\n` +
        `Coverage: ${result.learning_path.coverage_percentage}% ` +
        `(${result.learning_path.covered_topics.length}/${result.learning_path.covered_topics.length + result.learning_path.uncovered_topics.length} topics)\n\n` +
        `${result.learning_path.stages.length} learning stages created.`
      );
    } catch (error) {
      console.error('Error generating learning path:', error);
      setGeneratingPath(false);
      alert('❌ Failed to generate learning path. Please check your job description and try again.');
    }
  };

  if (loading) {
    return (
      <div className="home-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <div className="home-content">
        {/* Hero Section */}
        <div className="home-hero">
          <h1 className="home-title">🎯 Learning Path Creation</h1>
          <p className="home-subtitle">
            Tell us about your target job and we'll create a personalized learning path...
          </p>
        </div>

        {/* Form Section */}
        <div className="home-form">
          {/* Name Input */}
          <div className="form-group">
            <label className="form-label">Name</label>
            <input
              type="text"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="Enter your name"
              className="form-input"
            />
          </div>

          {/* Job Title (Optional) */}
          <div className="form-group">
            <label className="form-label">
              Job Title <span className="optional-tag">optional</span>
            </label>
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g., Quantitative Researcher"
              className="form-input"
            />
          </div>

          {/* Job Description */}
          <div className="form-group">
            <label className="form-label">
              Job Description <span className="required-tag">*</span>
              <span className="char-count">
                {jobDescription.length} characters
                {jobDescription.length < 20 && ` (minimum 20 required)`}
              </span>
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder={`Paste the full job posting here...\n\nExample:\nWe are seeking a quantitative researcher with expertise in:\n• Statistical modeling and time series analysis\n• Machine learning and deep learning\n• Python programming and data analysis\n• Stochastic calculus and probability theory\n• Strong mathematical background (linear algebra, calculus)\n\nResponsibilities:\n• Develop and implement quantitative trading strategies...\n• Analyze large datasets to identify market patterns...`}
              rows={10}
              className="form-textarea"
            />
          </div>

          {/* Seniority and Firm Row */}
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Seniority Level</label>
              <select
                value={jobSeniority}
                onChange={(e) => setJobSeniority(e.target.value)}
                className="form-select"
              >
                <option value="junior">Junior</option>
                <option value="mid">Mid-Level</option>
                <option value="senior">Senior</option>
                <option value="not_specified">Not Specified</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                Firm <span className="optional-tag">optional</span>
              </label>
              <input
                type="text"
                value={firm}
                onChange={(e) => setFirm(e.target.value)}
                placeholder="e.g., Two Sigma, Citadel..."
                className="form-input"
              />
            </div>
          </div>

          {/* Info Box */}
          <div className="info-box">
            <div className="info-header">ℹ️ What happens next:</div>
            <ul className="info-list">
              <li>AI analyzes your job requirements (5-10 seconds)</li>
              <li>Checks which topics are covered in our curated books</li>
              <li>Generates detailed learning structures for each topic (first time: 2-4 min, cached: instant!)</li>
              <li>Creates 3-5 learning stages tailored to your target role</li>
              <li>Provides external resources for topics not in our books</li>
            </ul>
          </div>

          {/* Generating State */}
          {generatingPath && (
            <div className="generating-notice">
              <div className="spinner"></div>
              <div>
                <strong>🤖 Analyzing Job & Generating Learning Path...</strong>
                <p>First time: 2-4 minutes (generating + caching structures for all topics)</p>
                <p>Next time: Instant! (retrieving from cache)</p>
              </div>
            </div>
          )}

          {/* Success State */}
          {learningPath && !generatingPath && (
            <div className="success-notice">
              <div className="success-icon">✅</div>
              <div className="success-content">
                <strong>Learning Path Generated!</strong>
                <p className="success-stats">
                  Coverage: <strong>{learningPath.coverage_percentage}%</strong> •{' '}
                  {learningPath.stages.length} learning stages created
                </p>
                <button
                  onClick={() => navigate('/learning-path')}
                  className="btn-view-path"
                >
                  View Learning Path →
                </button>
              </div>
            </div>
          )}

          {/* Generate Button */}
          <button
            onClick={handleGeneratePath}
            disabled={generatingPath || jobDescription.length < 20}
            className="btn-generate"
          >
            {generatingPath
              ? '🤖 Analyzing Job & Generating Path...'
              : '🚀 Generate My Learning Path'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Home;
