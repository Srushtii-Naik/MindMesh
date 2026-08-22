import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { NoteContentPreview } from '@/features/notes/markdown';

describe('NoteContentPreview', () => {
  it('shows a placeholder for empty content', () => {
    render(<NoteContentPreview content="" />);
    expect(screen.getByText('No content yet.')).toBeInTheDocument();
  });

  it('renders headings', () => {
    render(<NoteContentPreview content={'# Title\n## Subtitle'} />);
    expect(screen.getByRole('heading', { level: 1, name: 'Title' })).toBeInTheDocument();
  });

  it('renders bold and italic inline formatting without leaking asterisks', () => {
    render(<NoteContentPreview content="This is **bold** and this is *italic*." />);
    expect(screen.getByText('bold')).toBeInTheDocument();
    expect(screen.getByText('italic')).toBeInTheDocument();
  });

  it('renders list items as a list', () => {
    render(<NoteContentPreview content={'- First item\n- Second item'} />);
    const items = screen.getAllByRole('listitem');
    expect(items).toHaveLength(2);
    expect(items[0]).toHaveTextContent('First item');
    expect(items[1]).toHaveTextContent('Second item');
  });

  it('never injects raw HTML from note content', () => {
    render(<NoteContentPreview content="<script>window.__pwned = true;</script>" />);
    // Rendered as literal text, not executed or parsed as markup.
    expect(screen.getByText('<script>window.__pwned = true;</script>')).toBeInTheDocument();
  });
});
