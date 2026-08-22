import type { ReactNode } from 'react';

/**
 * A small, self-contained renderer for the constrained Markdown subset
 * notes support (ROADMAP.md Milestone 6: "Rich notes (formatted text)").
 *
 * PROJECT_RULES.md Section 2 locks the frontend dependency list, and no
 * rich-text editor library is on it — pulling one in would be exactly the
 * kind of ad-hoc stack substitution that section forbids. This renders a
 * safe subset (headings, bold/italic, lists) by building React elements
 * directly rather than via `dangerouslySetInnerHTML`, so there's no HTML
 * injection surface regardless of note content (PROJECT_RULES.md Section 8).
 *
 * Supported syntax: `# `/`## `/`### ` headings, `- `/`* ` list items,
 * `**bold**`, `*italic*`, and blank-line-separated paragraphs.
 */

const INLINE_PATTERN = /(\*\*[^*\n]+\*\*|\*[^*\n]+\*)/g;

function renderInline(text: string): ReactNode[] {
  return text.split(INLINE_PATTERN).map((segment, index) => {
    if (segment.startsWith('**') && segment.endsWith('**')) {
      return <strong key={index}>{segment.slice(2, -2)}</strong>;
    }
    if (segment.startsWith('*') && segment.endsWith('*')) {
      return <em key={index}>{segment.slice(1, -1)}</em>;
    }
    return <span key={index}>{segment}</span>;
  });
}

interface Block {
  type: 'h1' | 'h2' | 'h3' | 'ul' | 'p';
  lines: string[];
}

function parseBlocks(content: string): Block[] {
  const blocks: Block[] = [];
  let currentList: Block | null = null;

  for (const rawLine of content.split('\n')) {
    const line = rawLine.trimEnd();

    if (line.trim() === '') {
      currentList = null;
      continue;
    }

    if (line.startsWith('### ')) {
      currentList = null;
      blocks.push({ type: 'h3', lines: [line.slice(4)] });
    } else if (line.startsWith('## ')) {
      currentList = null;
      blocks.push({ type: 'h2', lines: [line.slice(3)] });
    } else if (line.startsWith('# ')) {
      currentList = null;
      blocks.push({ type: 'h1', lines: [line.slice(2)] });
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      const item = line.slice(2);
      if (currentList) {
        currentList.lines.push(item);
      } else {
        currentList = { type: 'ul', lines: [item] };
        blocks.push(currentList);
      }
    } else {
      currentList = null;
      const previous = blocks[blocks.length - 1];
      if (previous?.type === 'p') {
        previous.lines.push(line);
      } else {
        blocks.push({ type: 'p', lines: [line] });
      }
    }
  }

  return blocks;
}

/** Renders note content (a constrained Markdown subset) as formatted React elements. */
export function NoteContentPreview({ content }: { content: string }) {
  if (!content.trim()) {
    return <p className="italic text-slate-400 dark:text-slate-500">No content yet.</p>;
  }

  const blocks = parseBlocks(content);

  return (
    <div className="space-y-3">
      {blocks.map((block, index) => {
        if (block.type === 'h1') {
          return (
            <h1 key={index} className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              {renderInline(block.lines[0])}
            </h1>
          );
        }
        if (block.type === 'h2') {
          return (
            <h2 key={index} className="text-lg font-semibold text-slate-900 dark:text-slate-50">
              {renderInline(block.lines[0])}
            </h2>
          );
        }
        if (block.type === 'h3') {
          return (
            <h3 key={index} className="text-base font-semibold text-slate-900 dark:text-slate-50">
              {renderInline(block.lines[0])}
            </h3>
          );
        }
        if (block.type === 'ul') {
          return (
            <ul key={index} className="list-disc space-y-1 pl-5 text-slate-700 dark:text-slate-300">
              {block.lines.map((line, lineIndex) => (
                <li key={lineIndex}>{renderInline(line)}</li>
              ))}
            </ul>
          );
        }
        return (
          <p key={index} className="whitespace-pre-wrap text-slate-700 dark:text-slate-300">
            {block.lines.flatMap((line, lineIndex) => [
              lineIndex > 0 ? <br key={`br-${lineIndex}`} /> : null,
              ...renderInline(line),
            ])}
          </p>
        );
      })}
    </div>
  );
}
