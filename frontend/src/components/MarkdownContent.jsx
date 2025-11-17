import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import 'katex/dist/katex.min.css';
import '../styles/MarkdownContent.css';

const MarkdownContent = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
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
        // Style headers
        h1: ({ children }) => (
          <h1 className="markdown-h1">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="markdown-h2">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="markdown-h3">{children}</h3>
        ),
        // Style paragraphs
        p: ({ children }) => (
          <p className="markdown-p">{children}</p>
        ),
        // Style lists
        ul: ({ children }) => (
          <ul className="markdown-ul">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="markdown-ol">{children}</ol>
        ),
        li: ({ children }) => (
          <li className="markdown-li">{children}</li>
        ),
        // Style blockquotes
        blockquote: ({ children }) => (
          <blockquote className="markdown-blockquote">{children}</blockquote>
        ),
        // Style strong/bold
        strong: ({ children }) => (
          <strong className="markdown-strong">{children}</strong>
        ),
        // Style tables
        table: ({ children }) => (
          <div className="markdown-table-wrapper">
            <table className="markdown-table">{children}</table>
          </div>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

export default MarkdownContent;
