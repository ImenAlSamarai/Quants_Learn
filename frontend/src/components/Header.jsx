import { Brain } from 'lucide-react';

const Header = ({ categories, selectedCategory, onCategoryChange }) => {
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
    </header>
  );
};

export default Header;
