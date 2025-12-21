import { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/AdminPanel.css';

const AdminPanel = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadCategory, setUploadCategory] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/admin/stats');
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile || !uploadCategory) {
      alert('Please select a file and enter a category');
      return;
    }

    setUploading(true);

    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('category', uploadCategory);

    try {
      const response = await api.post('/api/admin/upload-content', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      alert(`✓ File uploaded successfully!\n\nNext step: Run indexing script to process the content:\npython backend/scripts/index_content.py`);
      setUploadFile(null);
      setUploadCategory('');
      e.target.reset();
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const clearCache = async () => {
    if (!confirm('Are you sure? This will clear ALL cached content. Content will be regenerated on next request.')) {
      return;
    }

    try {
      const response = await api.delete('/api/admin/cache');
      alert(response.data.message);
      fetchStats();
    } catch (error) {
      console.error('Error clearing cache:', error);
      alert('Failed to clear cache');
    }
  };

  if (loading) {
    return <div className="admin-panel"><div className="loading">Loading statistics...</div></div>;
  }

  return (
    <div className="admin-panel">
      <h1>📊 Admin Panel</h1>

      {/* Statistics Section */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats?.total_users || 0}</div>
          <div className="stat-label">Total Users</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats?.active_users_24h || 0}</div>
          <div className="stat-label">Active (24h)</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats?.total_queries || 0}</div>
          <div className="stat-label">Total Queries</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{((stats?.cache_hit_rate || 0) * 100).toFixed(1)}%</div>
          <div className="stat-label">Cache Hit Rate</div>
          <div className="stat-hint">💰 Cost savings from caching</div>
        </div>
      </div>

      {/* Most Accessed Topics */}
      <div className="section">
        <h2>🔥 Most Accessed Topics</h2>
        <div className="topics-list">
          {stats?.most_accessed_nodes?.slice(0, 5).map((node, index) => (
            <div key={node.node_id} className="topic-item">
              <div className="topic-rank">#{index + 1}</div>
              <div className="topic-info">
                <div className="topic-title">{node.title}</div>
                <div className="topic-count">{node.access_count} accesses</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Content Type Distribution */}
      <div className="section">
        <h2>📚 Content Type Distribution</h2>
        <div className="content-types">
          {Object.entries(stats?.popular_content_types || {}).map(([type, count]) => (
            <div key={type} className="content-type-item">
              <span className="type-icon">
                {type === 'explanation' ? '📖' :
                 type === 'example' ? '💡' :
                 type === 'quiz' ? '❓' :
                 type === 'visualization' ? '📊' : '📄'}
              </span>
              <span className="type-name">{type}</span>
              <span className="type-count">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Content Upload */}
      <div className="section">
        <h2>📤 Upload Content</h2>
        <form onSubmit={handleFileUpload} className="upload-form">
          <div className="form-group">
            <label>Category:</label>
            <input
              type="text"
              value={uploadCategory}
              onChange={(e) => setUploadCategory(e.target.value)}
              placeholder="e.g., linear_algebra, calculus, probability"
              required
            />
          </div>

          <div className="form-group">
            <label>File (Markdown or PDF):</label>
            <input
              type="file"
              accept=".md,.pdf,.txt"
              onChange={(e) => setUploadFile(e.target.files[0])}
              required
            />
          </div>

          <button type="submit" disabled={uploading} className="btn-primary">
            {uploading ? 'Uploading...' : 'Upload Content'}
          </button>
        </form>

        <div className="upload-hint">
          After uploading, run: <code>python backend/scripts/index_content.py</code>
        </div>
      </div>

      {/* Cache Management */}
      <div className="section">
        <h2>🗄️ Cache Management</h2>
        <p>Clear cached content to force regeneration with updated settings.</p>
        <button onClick={clearCache} className="btn-danger">
          Clear All Cache
        </button>
      </div>

      {/* Average Ratings by Difficulty */}
      {stats?.avg_rating_by_difficulty && Object.keys(stats.avg_rating_by_difficulty).length > 0 && (
        <div className="section">
          <h2>⭐ Content Quality by Difficulty Level</h2>
          <div className="ratings-list">
            {Object.entries(stats.avg_rating_by_difficulty).map(([level, rating]) => (
              <div key={level} className="rating-item">
                <span className="rating-level">Level {level}</span>
                <div className="rating-stars">
                  {'⭐'.repeat(Math.round(rating))}
                  {'☆'.repeat(5 - Math.round(rating))}
                </div>
                <span className="rating-value">{rating.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
