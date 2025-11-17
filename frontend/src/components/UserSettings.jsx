import { useState, useEffect } from 'react';
import useAppStore from '../store/useAppStore';
import '../styles/UserSettings.css';

const UserSettings = ({ userId, onClose }) => {
  const setLearningLevel = useAppStore((state) => state.setLearningLevel);
  const storedLevel = useAppStore((state) => state.learningLevel);
  const [userLevel, setUserLevel] = useState(storedLevel || 3);
  const [background, setBackground] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

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
        setUserLevel(data.learning_level);
        setBackground(data.background || '');
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);

    try {
      // Check if user exists, if not create
      let response = await fetch(`http://localhost:8000/api/users/${userId}`);

      if (!response.ok) {
        // Create new user
        response = await fetch('http://localhost:8000/api/users/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
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
            learning_level: userLevel,
            background: background
          })
        });
      }

      if (response.ok) {
        // Update the Zustand store with the new learning level
        setLearningLevel(userLevel);
        alert('✓ Settings saved! Future content will be tailored to your level.');
        onClose();
      } else {
        alert('Failed to save settings. Please try again.');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      // Even if backend fails, update the store for demo mode
      setLearningLevel(userLevel);
      alert('✓ Settings saved locally! Future content will be tailored to your level.');
      onClose();
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
            <h3>Your Learning Level</h3>
            <p className="section-description">
              Select your current level. Content difficulty and explanations will be tailored accordingly.
            </p>

            <div className="levels-grid">
              {levels.map((level) => (
                <div
                  key={level.level}
                  className={`level-card ${userLevel === level.level ? 'selected' : ''}`}
                  onClick={() => setUserLevel(level.level)}
                  style={{
                    borderColor: userLevel === level.level ? level.color : '#e2e8f0'
                  }}
                >
                  <div className="level-icon" style={{ color: level.color }}>
                    {level.icon}
                  </div>
                  <div className="level-info">
                    <div className="level-title">{level.title}</div>
                    <div className="level-description">{level.description}</div>
                  </div>
                  {userLevel === level.level && (
                    <div className="level-check" style={{ color: level.color }}>
                      ✓
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="setting-section">
            <h3>Background (Optional)</h3>
            <p className="section-description">
              Tell us about your background to get more personalized content.
            </p>
            <textarea
              value={background}
              onChange={(e) => setBackground(e.target.value)}
              placeholder="e.g., Physics PhD, Finance undergraduate, Self-taught programmer..."
              rows={3}
            />
          </div>

          <div className="cache-notice">
            <strong>📌 Note:</strong> Changing your level will show you different explanations.
            Previously cached content for other levels will remain available.
          </div>
        </div>

        <div className="settings-footer">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserSettings;
