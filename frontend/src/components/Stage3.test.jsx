import { render, screen } from '@testing-library/react';
import Stage3 from './Stage3';

describe('Stage3', () => {
  it('renders final response with chairman label', () => {
    render(
      <Stage3 finalResponse={{ model: 'chairman/model', response: 'final text' }} />
    );

    expect(screen.getByText(/Chairman/i)).toBeInTheDocument();
    expect(screen.getByText(/final text/i)).toBeInTheDocument();
  });

  it('returns null when missing finalResponse', () => {
    const { container } = render(<Stage3 finalResponse={null} />);
    expect(container.innerHTML).toBe('');
  });
});
