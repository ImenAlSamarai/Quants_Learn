import { useState } from 'react';
import { register } from '../../services/auth';
import '../../styles/Auth.css';

const Register = ({ onSuccess, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    user_id: '',
    password: '',
    confirmPassword: '',
    name: '',
    email: '',
    role: 'candidate',
  });

  // Candidate-specific fields
  const [candidateData, setCandidateData] = useState({
    cv_text: '',
    availability_date: '',
    willing_to_relocate: false,
  });

  // Recruiter-specific fields
  const [recruiterData, setRecruiterData] = useState({
    company_name: '',
    company_url: '',
    recruiter_type: 'internal',
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCandidateChange = (e) => {
    const { name, value, type, checked } = e.target;
    setCandidateData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleRecruiterChange = (e) => {
    const { name, value } = e.target;
    setRecruiterData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation
    if (!formData.user_id || !formData.password) {
      setError('Username and password are required');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      // Prepare registration data
      const registrationData = {
        user_id: formData.user_id,
        password: formData.password,
        name: formData.name || null,
        email: formData.email || null,
        role: formData.role,
      };

      // Add role-specific fields
      if (formData.role === 'candidate') {
        registrationData.cv_text = candidateData.cv_text || null;
        registrationData.availability_date = candidateData.availability_date || null;
        registrationData.willing_to_relocate = candidateData.willing_to_relocate;
      } else if (formData.role === 'recruiter') {
        registrationData.company_name = recruiterData.company_name || null;
        registrationData.company_url = recruiterData.company_url || null;
        registrationData.recruiter_type = recruiterData.recruiter_type || null;
      }

      const response = await register(registrationData);
      console.log('Registration successful:', response);

      // Call success callback if provided
      if (onSuccess) {
        onSuccess(response);
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Register</h2>
        <p className="auth-subtitle">Create your account on Quant Learning Platform</p>

        {error && (
          <div className="auth-error">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {/* Basic Information */}
          <div className="form-group">
            <label htmlFor="user_id">
              Username or Email <span className="required">*</span>
            </label>
            <input
              id="user_id"
              name="user_id"
              type="text"
              value={formData.user_id}
              onChange={handleChange}
              placeholder="Enter username or email"
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password <span className="required">*</span>
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="At least 8 characters"
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">
              Confirm Password <span className="required">*</span>
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Re-enter password"
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder="Your full name"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your.email@example.com"
              disabled={loading}
            />
          </div>

          {/* Role Selection */}
          <div className="form-group">
            <label htmlFor="role">
              Role <span className="required">*</span>
            </label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              disabled={loading}
              required
            >
              <option value="candidate">Candidate (Job Seeker)</option>
              <option value="recruiter">Recruiter</option>
            </select>
            <p className="form-help-text">
              {formData.role === 'candidate'
                ? 'Learn quantitative finance and prepare for job opportunities'
                : 'Find and connect with qualified candidates'}
            </p>
          </div>

          {/* Candidate-Specific Fields */}
          {formData.role === 'candidate' && (
            <div className="role-specific-fields">
              <h3 className="section-title">Candidate Information (Optional)</h3>

              <div className="form-group">
                <label htmlFor="availability_date">Availability Date</label>
                <input
                  id="availability_date"
                  name="availability_date"
                  type="date"
                  value={candidateData.availability_date}
                  onChange={handleCandidateChange}
                  disabled={loading}
                />
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="willing_to_relocate"
                    checked={candidateData.willing_to_relocate}
                    onChange={handleCandidateChange}
                    disabled={loading}
                  />
                  <span>Willing to relocate</span>
                </label>
              </div>
            </div>
          )}

          {/* Recruiter-Specific Fields */}
          {formData.role === 'recruiter' && (
            <div className="role-specific-fields">
              <h3 className="section-title">Recruiter Information (Optional)</h3>

              <div className="form-group">
                <label htmlFor="company_name">Company Name</label>
                <input
                  id="company_name"
                  name="company_name"
                  type="text"
                  value={recruiterData.company_name}
                  onChange={handleRecruiterChange}
                  placeholder="Your company name"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="company_url">Company Website</label>
                <input
                  id="company_url"
                  name="company_url"
                  type="url"
                  value={recruiterData.company_url}
                  onChange={handleRecruiterChange}
                  placeholder="https://www.example.com"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="recruiter_type">Recruiter Type</label>
                <select
                  id="recruiter_type"
                  name="recruiter_type"
                  value={recruiterData.recruiter_type}
                  onChange={handleRecruiterChange}
                  disabled={loading}
                >
                  <option value="internal">Internal Recruiter</option>
                  <option value="agency">Agency Recruiter</option>
                  <option value="headhunter">Headhunter</option>
                </select>
              </div>
            </div>
          )}

          <button type="submit" className="auth-button primary" disabled={loading}>
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an account?{' '}
            <button
              type="button"
              className="auth-link"
              onClick={onSwitchToLogin}
              disabled={loading}
            >
              Login here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
