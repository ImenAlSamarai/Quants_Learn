import { Brain, Settings, BarChart3 } from 'lucide-react';

const Header = ({ categories, selectedCategory, onCategoryChange, onShowSettings, onShowAdmin }) => {
  return (
    <header className="app-header">
      <div className="header-brand">
        <Brain size={28} color="#C9A96E" strokeWidth={2} />
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
          className="header-action-button"
        >
          <Settings size={16} />
          <span>Settings</span>
        </button>
        <button
          onClick={onShowAdmin}
          className="header-action-button header-action-button-primary"
        >
          <BarChart3 size={16} />
          <span>Admin</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
