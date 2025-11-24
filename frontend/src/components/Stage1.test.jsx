import { render, screen } from '@testing-library/react';
import Stage1 from './Stage1';

describe('Stage1', () => {
  it('renders tabs for each response', () => {
    const responses = [{ model: 'openai/gpt', response: 'hello' }];
    render(<Stage1 responses={responses} />);

    expect(screen.getByText('Stage 1: Individual Responses')).toBeInTheDocument();
    expect(screen.getByText('openai/gpt')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /gpt/i })).toBeInTheDocument();
  });

  it('returns null when no responses', () => {
    const { container } = render(<Stage1 responses={[]} />);
    expect(container.innerHTML).toBe('');
  });
});
