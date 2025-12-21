import { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/AdminPanel.css';

const AdminPanel = () => {
  const [stats, setStats] = useState(null);
  const [apiCosts, setApiCosts] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    fetchApiCosts();
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

  const fetchApiCosts = async () => {
    try {
      // Priority: env var (Railway), then localStorage (manual), then fallback
      const adminToken = import.meta.env.VITE_ADMIN_TOKEN ||
                        localStorage.getItem('adminToken') ||
                        'demo-token-change-in-production';

      console.log('Fetching API costs with token from:', import.meta.env.VITE_ADMIN_TOKEN ? 'env' : 'localStorage/fallback');

      const response = await api.get('/api/users/admin/api-costs', {
        headers: {
          'X-Admin-Token': adminToken
        }
      });
      setApiCosts(response.data);
    } catch (error) {
      console.error('Error fetching API costs:', error);
      console.error('Error details:', error.response?.data);
      // Set default empty data so section still shows
      setApiCosts({
        daily_cost_usd: 0,
        daily_calls: 0,
        daily_budget_usd: 10,
        budget_remaining_usd: 10,
        total_cost_usd: 0,
        total_calls: 0,
        by_model: {},
        by_operation: {},
        error: error.response?.data?.detail || 'Failed to load API costs'
      });
    }
  };

  const clearCache = async () => {
    if (!confirm('⚠️ WARNING: This will DELETE ALL cached content from the database!\n\n' +
      'This includes:\n' +
      '- All topic structures\n' +
      '- All section content\n' +
      '- All generated explanations\n\n' +
      'Next time users request content, it will be REGENERATED using AI ($$$ cost!).\n\n' +
      'Only do this if you changed prompts/logic and need fresh content.\n\n' +
      'Are you ABSOLUTELY SURE?')) {
      return;
    }

    try {
      const response = await api.delete('/api/admin/cache');
      alert(response.data.message + '\n\n⚠️ All content will now be regenerated on next user request (this costs money!)');
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
          <div className="stat-label">Total Content Views</div>
          <div className="stat-hint">Cached content accesses</div>
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

      {/* API Usage & Costs */}
      {apiCosts && (
        <div className="section">
          <h2>💰 API Usage & Costs</h2>

          {/* Daily Stats */}
          <div className="stats-grid" style={{marginBottom: '20px'}}>
            <div className="stat-card">
              <div className="stat-value">${apiCosts.daily_cost_usd || 0}</div>
              <div className="stat-label">Daily Cost</div>
              <div className="stat-hint">Budget: ${apiCosts.daily_budget_usd}</div>
            </div>

            <div className="stat-card">
              <div className="stat-value">{apiCosts.daily_calls || 0}</div>
              <div className="stat-label">Daily API Calls</div>
            </div>

            <div className="stat-card">
              <div className="stat-value">${apiCosts.budget_remaining_usd || 0}</div>
              <div className="stat-label">Budget Remaining</div>
            </div>

            <div className="stat-card">
              <div className="stat-value">${apiCosts.total_cost_usd || 0}</div>
              <div className="stat-label">Total Cost (All Time)</div>
              <div className="stat-hint">{apiCosts.total_calls} total calls</div>
            </div>
          </div>

          {/* Warning */}
          {apiCosts.warning && (
            <div className="warning-box" style={{
              background: '#fff3cd',
              border: '1px solid #ffc107',
              borderRadius: '8px',
              padding: '12px 16px',
              marginBottom: '20px',
              color: '#856404'
            }}>
              {apiCosts.warning}
            </div>
          )}

          {/* By Model Breakdown */}
          {apiCosts.by_model && Object.keys(apiCosts.by_model).length > 0 && (
            <div style={{marginBottom: '20px'}}>
              <h3 style={{fontSize: '16px', marginBottom: '12px'}}>📊 Usage by Model</h3>
              <div className="content-types">
                {Object.entries(apiCosts.by_model).map(([model, data]) => (
                  <div key={model} className="content-type-item">
                    <span className="type-icon">
                      {model.includes('claude') ? '🤖' :
                       model.includes('gpt-4') ? '🧠' :
                       model.includes('gpt-3.5') || model.includes('gpt-4o-mini') ? '⚡' : '🔧'}
                    </span>
                    <span className="type-name">{model}</span>
                    <span className="type-count">{data.calls} calls (${data.cost.toFixed(3)})</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* By Operation Breakdown */}
          {apiCosts.by_operation && Object.keys(apiCosts.by_operation).length > 0 && (
            <div>
              <h3 style={{fontSize: '16px', marginBottom: '12px'}}>🔧 Usage by Operation</h3>
              <div className="content-types">
                {Object.entries(apiCosts.by_operation).map(([operation, data]) => (
                  <div key={operation} className="content-type-item">
                    <span className="type-icon">
                      {operation.includes('structure') ? '📋' :
                       operation.includes('content') ? '📝' :
                       operation.includes('job') ? '💼' :
                       operation.includes('coverage') ? '🎯' : '⚙️'}
                    </span>
                    <span className="type-name">{operation}</span>
                    <span className="type-count">{data.calls} calls (${data.cost.toFixed(3)})</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
