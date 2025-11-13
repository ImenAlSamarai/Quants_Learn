import { useState } from 'react';
import Plot from 'react-plotly.js';

const Visualization = ({ config }) => {
  const [parameters, setParameters] = useState(() => {
    const initialParams = {};
    if (config.parameters) {
      Object.entries(config.parameters).forEach(([key, param]) => {
        initialParams[key] = param.default || 0;
      });
    }
    return initialParams;
  });

  const handleParameterChange = (paramName, value) => {
    setParameters(prev => ({ ...prev, [paramName]: parseFloat(value) }));
  };

  const generatePlotData = () => {
    // This is a simplified visualization generator
    // In a real implementation, you'd use the config.code_template
    // or have specific visualization functions

    const { visualization_type } = config;

    if (visualization_type === 'plot_2d') {
      // Example: Plot a function
      const x = Array.from({ length: 100 }, (_, i) => i / 10);
      const y = x.map(val => Math.sin(val * (parameters.frequency || 1)) * (parameters.amplitude || 1));

      return [{
        x,
        y,
        type: 'scatter',
        mode: 'lines',
        line: { color: '#3b82f6', width: 2 },
      }];
    } else if (visualization_type === 'plot_3d') {
      // Example: 3D surface
      const size = 20;
      const x = Array.from({ length: size }, (_, i) => i - size / 2);
      const y = Array.from({ length: size }, (_, i) => i - size / 2);
      const z = x.map(xi => y.map(yi => Math.sin(Math.sqrt(xi * xi + yi * yi))));

      return [{
        x,
        y,
        z,
        type: 'surface',
        colorscale: 'Viridis',
      }];
    } else if (visualization_type === 'matrix') {
      // Example: Heatmap
      const matrix = [
        [1, 0.5, 0.3],
        [0.5, 1, 0.6],
        [0.3, 0.6, 1],
      ];

      return [{
        z: matrix,
        type: 'heatmap',
        colorscale: 'RdBu',
      }];
    }

    // Default: simple line plot
    const x = Array.from({ length: 50 }, (_, i) => i);
    const y = x.map(val => val * (parameters.slope || 1));

    return [{
      x,
      y,
      type: 'scatter',
      mode: 'lines+markers',
    }];
  };

  return (
    <div className="visualization-container">
      <div className="viz-header">
        <h3>{config.title || 'Interactive Visualization'}</h3>
        <p className="viz-description">{config.description}</p>
      </div>

      {config.parameters && Object.keys(config.parameters).length > 0 && (
        <div className="viz-controls">
          <h4>Controls</h4>
          <div className="parameter-grid">
            {Object.entries(config.parameters).map(([paramName, param]) => (
              <div key={paramName} className="parameter-control">
                <label>
                  {param.label || paramName}
                  <span className="param-value">{parameters[paramName]?.toFixed(2)}</span>
                </label>
                {param.type === 'slider' ? (
                  <input
                    type="range"
                    min={param.min || 0}
                    max={param.max || 10}
                    step={(param.max - param.min) / 100 || 0.1}
                    value={parameters[paramName] || param.default}
                    onChange={(e) => handleParameterChange(paramName, e.target.value)}
                    className="slider"
                  />
                ) : (
                  <input
                    type="number"
                    min={param.min}
                    max={param.max}
                    value={parameters[paramName] || param.default}
                    onChange={(e) => handleParameterChange(paramName, e.target.value)}
                    className="number-input"
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="viz-plot">
        <Plot
          data={generatePlotData()}
          layout={{
            autosize: true,
            paper_bgcolor: '#1e293b',
            plot_bgcolor: '#1e293b',
            font: { color: '#fff' },
            xaxis: { gridcolor: '#334155' },
            yaxis: { gridcolor: '#334155' },
            margin: { l: 50, r: 50, t: 50, b: 50 },
          }}
          config={{
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
          }}
          style={{ width: '100%', height: '500px' }}
        />
      </div>

      {config.code_template && (
        <div className="viz-code">
          <h4>Code Template</h4>
          <pre><code>{config.code_template}</code></pre>
        </div>
      )}
    </div>
  );
};

export default Visualization;
