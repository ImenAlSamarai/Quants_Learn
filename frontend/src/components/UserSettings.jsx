import { useState, useEffect } from 'react';
import useAppStore from '../store/useAppStore';
import { updateJobProfile } from '../services/api';
import '../styles/UserSettings.css';

const UserSettings = ({ userId, onClose }) => {
  const setLearningLevel = useAppStore((state) => state.setLearningLevel);
  const storedLevel = useAppStore((state) => state.learningLevel);
  const [userName, setUserName] = useState('');
  const [userLevel, setUserLevel] = useState(storedLevel || 3);
  const [background, setBackground] = useState('');

  // Phase 2.5: Job-based personalization fields
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobSeniority, setJobSeniority] = useState('mid');
  const [firm, setFirm] = useState('');

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generatingPath, setGeneratingPath] = useState(false);
  const [learningPath, setLearningPath] = useState(null);

  const levels = [
    {
      level: 1,
      title: 'Undergraduate - New to Quant Finance',
      description: 'Simple explanations, everyday analogies, minimal equations',
      icon: '🌱',
      color: '#10b981'
    },
    {
      level: 2,
      title: 'Undergraduate - Foundation',
      description: 'Balance of intuition and formalism, some math background',
      icon: '📚',
      color: '#3b82f6'
    },
    {
      level: 3,
      title: 'Graduate Student',
      description: 'Strong math background, balanced rigor and intuition',
      icon: '🎓',
      color: '#8b5cf6'
    },
    {
      level: 4,
      title: 'PhD Researcher',
      description: 'Research-level examples, cutting-edge applications',
      icon: '🔬',
      color: '#ec4899'
    },
    {
      level: 5,
      title: 'Experienced Researcher',
      description: 'Technical depth, latest research, production implementations',
      icon: '⭐',
      color: '#ef4444'
    }
  ];

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/users/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setUserName(data.name || '');
        setUserLevel(data.learning_level);
        setBackground(data.background || '');

        // Phase 2.5: Load job fields if they exist
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
    setSaving(true);
    setGeneratingPath(false);
    setLearningPath(null);

    try {
      // Phase 2.5: If job description is provided, use job-based API
      if (jobDescription && jobDescription.trim().length > 20) {
        setGeneratingPath(true);

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
      } else {
        // Fallback: Use old difficulty-based API
        let response = await fetch(`http://localhost:8000/api/users/${userId}`);

        if (!response.ok) {
          // Create new user
          response = await fetch('http://localhost:8000/api/users/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user_id: userId,
              name: userName,
              learning_level: userLevel,
              background: background
            })
          });
        } else {
          // Update existing user
          response = await fetch(`http://localhost:8000/api/users/${userId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              name: userName,
              learning_level: userLevel,
              background: background
            })
          });
        }

        if (response.ok) {
          setLearningLevel(userLevel);
          alert('✓ Settings saved! Future content will be tailored to your level.');
        } else {
          alert('Failed to save settings. Please try again.');
        }
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      setGeneratingPath(false);
      alert('Error saving settings. Please check console for details.');
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
          <h2>⚙️ Learning Preferences</h2>
          <button onClick={onClose} className="close-btn">×</button>
        </div>

        <div className="settings-body">
          <div className="setting-section">
            <h3>Your Name</h3>
            <p className="section-description">
              Enter your name to personalize your learning experience.
            </p>
            <input
              type="text"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="Enter your name"
              className="name-input"
            />
          </div>

          <div className="setting-section">
            <h3>🎯 Your Target Job</h3>
            <p className="section-description">
              Paste the full job description you're targeting. We'll generate a personalized learning path tailored to the specific requirements.
            </p>

            <label>Job Title</label>
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g., Quantitative Researcher, Quant Trader, ML Engineer..."
              className="job-input"
            />

            <label>Job Description *</label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the full job posting here. Include requirements, responsibilities, and qualifications.&#10;&#10;Example:&#10;We are seeking a quantitative researcher with strong skills in statistical modeling, time series analysis, machine learning, and Python programming..."
              rows={8}
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

          <div className="cache-notice">
            <strong>💡 Tip:</strong> Paste the complete job posting for best results.
            The system will identify which topics are covered in our books and which require external resources.
          </div>
        </div>

        <div className="settings-footer">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={handleSave} disabled={saving || generatingPath} className="btn-primary">
            {generatingPath ? '🤖 Generating Path...' : saving ? 'Saving...' : 'Save Job Profile & Generate Path'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserSettings;
