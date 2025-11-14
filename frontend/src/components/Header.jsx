import { Brain } from 'lucide-react';

const Header = ({ categories, selectedCategory, onCategoryChange, onShowSettings, onShowAdmin }) => {
  return (
    <header className="app-header">
      <div className="header-brand">
        <Brain size={32} />
        <div>
          <h1>Quant Learning Platform</h1>
          <p>Master quantitative finance through interactive exploration</p>
        </div>
      </div>

      <nav className="category-nav">
        <button
          className={`category-button ${!selectedCategory ? 'active' : ''}`}
          onClick={() => onCategoryChange(null)}
        >
          All Topics
        </button>
        {categories.map(cat => (
          <button
            key={cat.id}
            className={`category-button ${selectedCategory === cat.id ? 'active' : ''}`}
            onClick={() => onCategoryChange(cat.id)}
            style={{ borderLeftColor: cat.color }}
          >
            <span className="category-icon">{cat.icon}</span>
            <span>{cat.name}</span>
          </button>
        ))}
      </nav>

      <div style={{
        display: 'flex',
        gap: '0.75rem',
        marginLeft: 'auto'
      }}>
        <button
          onClick={onShowSettings}
          style={{
            background: 'rgba(51, 65, 85, 0.5)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            color: '#f1f5f9',
            border: '1px solid rgba(148, 163, 184, 0.3)',
            padding: '0.75rem 1.5rem',
            borderRadius: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            fontSize: '0.9rem'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 8px 30px rgba(59, 130, 246, 0.3)';
            e.target.style.borderColor = 'rgba(59, 130, 246, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
            e.target.style.borderColor = 'rgba(148, 163, 184, 0.3)';
          }}
        >
          ⚙️ Settings
        </button>
        <button
          onClick={onShowAdmin}
          style={{
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.8) 0%, rgba(139, 92, 246, 0.8) 100%)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            color: 'white',
            border: '1px solid rgba(59, 130, 246, 0.5)',
            padding: '0.75rem 1.5rem',
            borderRadius: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(59, 130, 246, 0.3)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            fontSize: '0.9rem'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 8px 40px rgba(59, 130, 246, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 4px 20px rgba(59, 130, 246, 0.3)';
          }}
        >
          📊 Admin Panel
        </button>
      </div>
    </header>
  );
};

export default Header;
