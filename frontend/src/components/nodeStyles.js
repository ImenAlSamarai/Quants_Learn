// Modern Zen Color Palette - Easy to modify
export const colors = {
  // Background
  background: '#FAFAFA',

  // Category colors (soft, neutral tones)
  categories: {
    linear_algebra: {
      light: '#E0E7FF',
      main: '#818CF8',
      dark: '#6366F1',
    },
    calculus: {
      light: '#D1FAE5',
      main: '#6EE7B7',
      dark: '#10B981',
    },
    probability: {
      light: '#FED7AA',
      main: '#FDBA74',
      dark: '#F97316',
    },
    statistics: {
      light: '#FBCFE8',
      main: '#F9A8D4',
      dark: '#EC4899',
    },
  },

  // Difficulty-based accents
  difficulty: {
    1: '#10B981', // Green - Fundamentals
    2: '#3B82F6', // Blue - Core
    3: '#8B5CF6', // Purple - Intermediate
    4: '#EC4899', // Pink - Advanced
    5: '#EF4444', // Red - Expert
  },

  // Neutral colors
  node: {
    background: '#FFFFFF',
    border: '#E5E7EB',
    text: '#1F2937',
    textSecondary: '#6B7280',
  },

  // Effects
  shadow: 'rgba(0, 0, 0, 0.05)',
  shadowHover: 'rgba(0, 0, 0, 0.1)',
  glow: 'rgba(99, 102, 241, 0.2)',
};

// Node styling configuration
export const nodeStyles = {
  // Base dimensions
  rootNode: {
    width: 180,
    height: 180,
    borderRadius: 20,
  },
  childNode: {
    width: 140,
    height: 140,
    borderRadius: 16,
  },

  // Spacing
  padding: 20,
  iconSize: 32,

  // Effects
  shadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
  shadowHover: '0 8px 24px rgba(0, 0, 0, 0.12)',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',

  // Border
  borderWidth: 2,
  borderStyle: 'solid',
};

// Edge styling configuration
export const edgeStyles = {
  stroke: '#94A3B8',
  strokeWidth: 2,
  strokeWidthHover: 3,

  // Direct prerequisite
  direct: {
    stroke: '#3B82F6',
    strokeWidth: 2.5,
    opacity: 0.6,
  },

  // Indirect/optional
  indirect: {
    stroke: '#94A3B8',
    strokeWidth: 1.5,
    opacity: 0.3,
    dashArray: '5,5',
  },
};

// Layout configuration for radial clustering
export const layoutConfig = {
  radius: 350,
  centerX: 0,
  centerY: 0,
  categories: ['linear_algebra', 'calculus', 'probability', 'statistics'],
};
