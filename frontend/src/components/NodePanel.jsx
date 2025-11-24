import { useState, useEffect } from 'react';
import { X, BookOpen, Code, Brain, PlayCircle } from 'lucide-react';
import { queryContent } from '../services/api';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import Quiz from './Quiz';
import Visualization from './Visualization';

const NodePanel = ({ node, userId, onClose }) => {
  const [activeTab, setActiveTab] = useState('explanation');
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadContent('explanation');
  }, [node]);

  const loadContent = async (contentType) => {
    setLoading(true);
    try {
      const data = await queryContent(node.id, contentType);
      setContent(data);
    } catch (error) {
      console.error('Error loading content:', error);
      setContent({
        generated_content: 'Error loading content. Please try again.',
        related_topics: [],
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    loadContent(tab);
  };

  const tabs = [
    { id: 'explanation', label: 'Explanation', icon: BookOpen },
    { id: 'example', label: 'Examples', icon: Code },
    { id: 'quiz', label: 'Quiz', icon: Brain },
    { id: 'visualization', label: 'Visualize', icon: PlayCircle },
  ];

  return (
    <div className="node-panel">
      <div className="panel-header">
        <div className="panel-title">
          <span className="node-icon">{node.icon}</span>
          <div>
            <h2>{node.title}</h2>
            <p className="node-category">
              {node.category} • Difficulty: {'⭐'.repeat(node.difficulty_level || 1)}
            </p>
          </div>
        </div>
        <button className="close-button" onClick={onClose}>
          <X size={24} />
        </button>
      </div>

      <div className="panel-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => handleTabChange(tab.id)}
          >
            <tab.icon size={18} />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="panel-content">
        {loading ? (
          <div className="loading-content">
            <div className="spinner"></div>
            <p>Generating content...</p>
          </div>
        ) : content ? (
          <>
            {activeTab === 'quiz' && content.interactive_component?.type === 'quiz' ? (
              <Quiz
                questions={content.interactive_component.questions}
                nodeId={node.id}
                userId={userId}
              />
            ) : activeTab === 'visualization' && content.interactive_component?.type === 'visualization' ? (
              <Visualization config={content.interactive_component.config} />
            ) : (
              <div className="content-body">
                <ReactMarkdown
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={vscDarkPlus}
                          language={match[1]}
                          PreTag="div"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {content.generated_content}
                </ReactMarkdown>

                {content.interactive_component?.type === 'code_editor' && (
                  <div className="code-playground">
                    <h3>Try it yourself:</h3>
                    <SyntaxHighlighter
                      language="python"
                      style={vscDarkPlus}
                      showLineNumbers
                    >
                      {content.interactive_component.code}
                    </SyntaxHighlighter>
                    <p className="code-hint">
                      💡 Copy this code to your Python environment to experiment!
                    </p>
                  </div>
                )}
              </div>
            )}

            {content.related_topics && content.related_topics.length > 0 && (
              <div className="related-topics">
                <h3>🔗 Related Topics</h3>
                <div className="topic-chips">
                  {content.related_topics.map((topic, idx) => (
                    <span key={idx} className="topic-chip">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="empty-content">
            <p>No content available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NodePanel;
