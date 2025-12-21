import { useState, useEffect } from 'react';
import useAppStore from '../store/useAppStore';
import { updateJobProfile } from '../services/api';
import api from '../services/api';
import '../styles/UserSettings.css';

const UserSettings = ({ userId, onClose }) => {
  const [userName, setUserName] = useState('');

  // Job-based personalization fields
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobSeniority, setJobSeniority] = useState('mid');
  const [firm, setFirm] = useState('');

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generatingPath, setGeneratingPath] = useState(false);
  const [learningPath, setLearningPath] = useState(null);

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await api.get(`/api/users/${encodeURIComponent(userId)}`);
      const data = response.data;
        setUserName(data.name || '');

        // Load job fields if they exist
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

  const handleSave = async () => {
    // Validation
    if (!jobDescription || jobDescription.trim().length < 20) {
      alert('⚠️ Please provide a job description (at least 20 characters) to generate your personalized learning path.');
      return;
    }

    setSaving(true);
    setGeneratingPath(true);
    setLearningPath(null);

    try {
      const result = await updateJobProfile(userId, {
        job_title: jobTitle,
        job_description: jobDescription,
        job_seniority: jobSeniority,
        firm: firm || undefined,
      });

      setGeneratingPath(false);
      setLearningPath(result.learning_path);

      alert(
        `✓ Job profile saved and learning path generated!\n\n` +
        `Coverage: ${result.learning_path.coverage_percentage}% ` +
        `(${result.learning_path.covered_topics.length}/${result.learning_path.covered_topics.length + result.learning_path.uncovered_topics.length} topics)\n\n` +
        `${result.learning_path.stages.length} learning stages created.`
      );
    } catch (error) {
      console.error('Error saving job profile:', error);
      setGeneratingPath(false);
      alert('❌ Failed to generate learning path. Please check your job description and try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="settings-modal">
        <div className="settings-content">
          <div className="loading">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-modal" onClick={onClose}>
      <div className="settings-content" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>🎯 Job-Based Learning Path</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>

        <div className="settings-body">
          <div className="intro-message">
            <p>
              <strong>Tell us about your target job</strong> and we'll create a personalized learning path
              with topics from our curated books and external resources for any gaps.
            </p>
          </div>

          <div className="setting-section">
            <h3>Your Name</h3>
            <input
              type="text"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="Enter your name"
              className="name-input"
            />
          </div>

          <div className="setting-section job-section">
            <h3>📋 Job Description</h3>
            <p className="section-description">
              <strong>Paste the complete job posting</strong> you're targeting. Our AI will analyze the requirements
              and create a customized learning path showing what's covered in our books and what needs external resources.
            </p>

            <label>Job Title (Optional)</label>
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g., Quantitative Researcher"
              className="job-input"
            />

            <label>
              Job Description <span className="required">*</span>
              <span className="char-count">
                {jobDescription.length} characters
                {jobDescription.length < 20 && ` (minimum 20 required)`}
              </span>
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the full job posting here...&#10;&#10;Example:&#10;We are seeking a quantitative researcher with expertise in:&#10;• Statistical modeling and time series analysis&#10;• Machine learning and deep learning&#10;• Python programming and data analysis&#10;• Stochastic calculus and probability theory&#10;• Strong mathematical background (linear algebra, calculus)&#10;&#10;Responsibilities:&#10;• Develop and implement quantitative trading strategies...&#10;• Analyze large datasets to identify market patterns...&#10;• Collaborate with traders and portfolio managers..."
              rows={10}
              className="job-description-textarea"
              style={{ width: '100%', marginBottom: '1rem' }}
            />

            <div style={{ display: 'flex', gap: '1rem' }}>
              <div style={{ flex: 1 }}>
                <label>Seniority Level</label>
                <select
                  value={jobSeniority}
                  onChange={(e) => setJobSeniority(e.target.value)}
                  className="seniority-select"
                >
                  <option value="junior">Junior</option>
                  <option value="mid">Mid-Level</option>
                  <option value="senior">Senior</option>
                  <option value="not_specified">Not Specified</option>
                </select>
              </div>

              <div style={{ flex: 1 }}>
                <label>Firm (Optional)</label>
                <input
                  type="text"
                  value={firm}
                  onChange={(e) => setFirm(e.target.value)}
                  placeholder="e.g., Two Sigma, Citadel..."
                  className="firm-input"
                />
              </div>
            </div>
          </div>

          {generatingPath && (
            <div className="generating-notice">
              <div className="spinner"></div>
              <strong>🤖 Analyzing job description and generating learning path...</strong>
              <p>This may take 5-10 seconds.</p>
            </div>
          )}

          {learningPath && (
            <div className="success-notice">
              <strong>✅ Learning Path Generated!</strong>
              <p>
                Coverage: <strong>{learningPath.coverage_percentage}%</strong>
                ({learningPath.covered_topics.length}/{learningPath.covered_topics.length + learningPath.uncovered_topics.length} topics)
              </p>
              <p>
                {learningPath.stages.length} learning stages created tailored to your target role.
              </p>
              <button
                onClick={() => window.location.href = '/learning-path'}
                className="btn-view-path"
              >
                View Learning Path →
              </button>
            </div>
          )}

          <div className="info-box">
            <strong>ℹ️ What happens next:</strong>
            <ul>
              <li>AI analyzes your job requirements (5-10 seconds)</li>
              <li>Checks which topics are covered in our curated books</li>
              <li>Creates 3-5 learning stages tailored to your target role</li>
              <li>Provides external resources for topics not in our books</li>
            </ul>
          </div>
        </div>

        <div className="settings-footer">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving || generatingPath || jobDescription.length < 20}
            className="btn-primary"
          >
            {generatingPath ? '🤖 Analyzing Job & Generating Path...' : saving ? 'Saving...' : '🚀 Generate My Learning Path'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserSettings;
