import { render, screen } from '@testing-library/react';
import Stage2 from './Stage2';

describe('Stage2', () => {
  it('shows parsed and aggregate rankings with model names', () => {
    const rankings = [
      {
        model: 'openai/gpt',
        ranking: 'FINAL RANKING:\n1. Response A',
        parsed_ranking: ['Response A'],
      },
    ];
    const labelToModel = { 'Response A': 'openai/gpt' };
    const aggregateRankings = [
      { model: 'openai/gpt', average_rank: 1.0, rankings_count: 1 },
    ];

    render(
      <Stage2
        rankings={rankings}
        labelToModel={labelToModel}
        aggregateRankings={aggregateRankings}
      />
    );

    expect(screen.getByText('Stage 2: Peer Rankings')).toBeInTheDocument();
    expect(screen.getByText(/Aggregate Rankings/)).toBeInTheDocument();
    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getAllByText('gpt').length).toBeGreaterThan(0);
  });

  it('returns null when rankings missing', () => {
    const { container } = render(
      <Stage2 rankings={[]} labelToModel={{}} aggregateRankings={[]} />
    );
    expect(container.innerHTML).toBe('');
  });
});
