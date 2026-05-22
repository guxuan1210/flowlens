import ReactMarkdown from 'react-markdown'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css'

interface MarkdownReportProps {
  content: string
  className?: string
}

export function MarkdownReport({ content, className }: MarkdownReportProps) {
  if (!content) {
    return <p className="text-muted-foreground text-sm italic">No content available.</p>
  }

  return (
    <div className={`prose prose-invert prose-sm max-w-none prose-headings:text-foreground prose-code:text-sky-300 prose-a:text-sky-400 ${className || ''}`}>
      <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
        {content}
      </ReactMarkdown>
    </div>
  )
}
