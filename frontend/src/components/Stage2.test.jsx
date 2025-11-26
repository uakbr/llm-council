import { render, screen, fireEvent } from '@testing-library/react';
import Stage2 from './Stage2';

const rankings = [
  {
    model: 'openai/gpt-5.1',
    ranking: 'Response A is better than Response B',
    parsed_ranking: ['Response A', 'Response B'],
  },
  {
    model: 'google/gemini-3-pro-preview',
    ranking: 'Response B wins',
    parsed_ranking: ['Response B'],
  },
];

const labelToModel = {
  'Response A': 'openai/gpt-5.1',
  'Response B': 'google/gemini-3-pro-preview',
};

describe('Stage2', () => {
  it('renders tablist and panels with rankings', () => {
    render(<Stage2 rankings={rankings} labelToModel={labelToModel} aggregateRankings={[]} />);
    expect(screen.getAllByRole('tab')).toHaveLength(2);
    expect(screen.getByRole('tabpanel')).toHaveTextContent('gpt-5.1');
  });

  it('switches tabs and shows corresponding content', () => {
    render(<Stage2 rankings={rankings} labelToModel={labelToModel} aggregateRankings={[]} />);
    fireEvent.click(screen.getAllByRole('tab')[1]);
    expect(screen.getByRole('tabpanel')).toHaveTextContent('wins');
  });
});
