import { Network, GitBranch, Target } from 'lucide-react';

const LayoutSelector = ({ currentLayout, onLayoutChange }) => {
  const layouts = [
    {
      id: 'force',
      name: 'Force-Directed',
      icon: Network,
      description: 'Physics-based organic layout'
    },
    {
      id: 'dag',
      name: 'Hierarchical DAG',
      icon: GitBranch,
      description: 'Top-down prerequisite flow'
    },
    {
      id: 'radial',
      name: 'Radial Clusters',
      icon: Target,
      description: 'Category-based islands'
    }
  ];

  return (
    <div style={{
      position: 'absolute',
      top: '1rem',
      left: '1rem',
      zIndex: 100,
      background: 'rgba(15, 23, 42, 0.8)',
      backdropFilter: 'blur(10px)',
      WebkitBackdropFilter: 'blur(10px)',
      borderRadius: '12px',
      padding: '0.5rem',
      border: '1px solid rgba(148, 163, 184, 0.2)',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
    }}>
      <div style={{
        fontSize: '0.75rem',
        color: '#94a3b8',
        marginBottom: '0.5rem',
        paddingLeft: '0.5rem',
        fontWeight: '600'
      }}>
        LAYOUT MODE
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', flexDirection: 'column' }}>
        {layouts.map(layout => {
          const Icon = layout.icon;
          const isActive = currentLayout === layout.id;

          return (
            <button
              key={layout.id}
              onClick={() => onLayoutChange(layout.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.75rem 1rem',
                background: isActive
                  ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.4) 0%, rgba(139, 92, 246, 0.4) 100%)'
                  : 'rgba(51, 65, 85, 0.5)',
                color: isActive ? '#ffffff' : '#cbd5e1',
                border: isActive
                  ? '1px solid rgba(59, 130, 246, 0.5)'
                  : '1px solid rgba(148, 163, 184, 0.2)',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                fontSize: '0.875rem',
                fontWeight: isActive ? '600' : '500',
                minWidth: '200px',
                textAlign: 'left'
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.target.style.background = 'rgba(71, 85, 105, 0.6)';
                  e.target.style.borderColor = 'rgba(148, 163, 184, 0.4)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.target.style.background = 'rgba(51, 65, 85, 0.5)';
                  e.target.style.borderColor = 'rgba(148, 163, 184, 0.2)';
                }
              }}
            >
              <Icon size={18} style={{ flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <div>{layout.name}</div>
                <div style={{
                  fontSize: '0.7rem',
                  color: isActive ? '#e0e7ff' : '#94a3b8',
                  marginTop: '0.125rem'
                }}>
                  {layout.description}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default LayoutSelector;
