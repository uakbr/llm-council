import { render, screen, fireEvent } from '@testing-library/react';
import Stage1 from './Stage1';

const responses = [
  { model: 'openai/gpt-5.1', response: 'Answer A' },
  { model: 'google/gemini-3-pro-preview', response: 'Answer B' },
];

describe('Stage1', () => {
  it('renders tabs with accessible roles', () => {
    render(<Stage1 responses={responses} />);
    const tabs = screen.getAllByRole('tab');
    expect(tabs).toHaveLength(2);
    expect(screen.getByRole('tabpanel')).toBeInTheDocument();
  });

  it('switches content when selecting another tab', () => {
    render(<Stage1 responses={responses} />);
    fireEvent.click(screen.getAllByRole('tab')[1]);
    expect(screen.getByRole('tabpanel')).toHaveTextContent('Answer B');
  });
});
