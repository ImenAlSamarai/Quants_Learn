import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { colors, nodeStyles } from './nodeStyles';

const CustomNode = ({ data, selected }) => {
  const isRoot = data.isRoot;
  const category = data.category || 'linear_algebra';
  const difficulty = data.difficulty || 1;

  // Get category colors
  const categoryColors = colors.categories[category] || colors.categories.linear_algebra;

  // Determine node size
  const size = isRoot ? nodeStyles.rootNode : nodeStyles.childNode;

  // Node style
  const nodeStyle = {
    width: `${size.width}px`,
    height: `${size.height}px`,
    borderRadius: `${size.borderRadius}px`,
    background: `linear-gradient(135deg, ${categoryColors.light} 0%, ${colors.node.background} 100%)`,
    border: `${nodeStyles.borderWidth}px ${nodeStyles.borderStyle} ${selected ? categoryColors.dark : categoryColors.main}`,
    boxShadow: selected ? nodeStyles.shadowHover : nodeStyles.shadow,
    transition: nodeStyles.transition,
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: `${nodeStyles.padding}px`,
    position: 'relative',
    overflow: 'hidden',
  };

  // Icon style
  const iconStyle = {
    fontSize: `${nodeStyles.iconSize}px`,
    marginBottom: '12px',
    filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))',
  };

  // Title style
  const titleStyle = {
    fontSize: isRoot ? '16px' : '14px',
    fontWeight: '600',
    color: colors.node.text,
    textAlign: 'center',
    lineHeight: '1.4',
    marginBottom: isRoot ? '8px' : '4px',
  };

  // Description style (only for root nodes)
  const descriptionStyle = {
    fontSize: '12px',
    fontWeight: '400',
    color: colors.node.textSecondary,
    textAlign: 'center',
    lineHeight: '1.3',
    maxWidth: '90%',
  };

  // Difficulty badge style
  const badgeStyle = {
    position: 'absolute',
    top: '8px',
    right: '8px',
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    background: colors.difficulty[difficulty],
    color: '#FFFFFF',
    fontSize: '11px',
    fontWeight: '700',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  };

  // Accent bar at the bottom
  const accentStyle = {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '4px',
    background: `linear-gradient(90deg, ${categoryColors.main} 0%, ${categoryColors.dark} 100%)`,
  };

  return (
    <div style={nodeStyle} className="custom-node">
      {/* Handles for connections */}
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />

      {/* Difficulty badge */}
      <div style={badgeStyle}>{difficulty}</div>

      {/* Icon */}
      <div style={iconStyle}>{data.icon || '📚'}</div>

      {/* Title */}
      <div style={titleStyle}>{data.label}</div>

      {/* Description (root nodes only) */}
      {isRoot && data.description && (
        <div style={descriptionStyle}>
          {data.description.substring(0, 60)}...
        </div>
      )}

      {/* Accent bar */}
      <div style={accentStyle} />
    </div>
  );
};

export default memo(CustomNode);
