import { CandidateDestination } from '@/lib/types';

interface DestinationComparisonProps {
  candidates: CandidateDestination[];
  selectedName?: string;
}

export default function DestinationComparison({ candidates, selectedName }: DestinationComparisonProps) {
  if (!candidates || candidates.length === 0) return null;

  return (
    <div className="w-full max-w-5xl mx-auto my-16">
      <div className="text-center mb-10">
        <h2 className="font-serif text-3xl text-roam-ink">Destination Analysis</h2>
        <p className="font-mono text-sm text-roam-ink-light mt-2">COMPARING TOP CANDIDATES</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {candidates.map((candidate, idx) => {
          const isSelected = selectedName === candidate.name || candidate.selected;
          const isRejected = !isSelected && candidate.rejected_reason;
          
          return (
            <div 
              key={idx} 
              className={`p-6 border-2 transition-all ${
                isSelected 
                  ? 'border-roam-green bg-roam-ivory shadow-[4px_4px_0px_0px_rgba(27,67,50,1)]' 
                  : 'border-roam-gray bg-white opacity-80 hover:opacity-100'
              }`}
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-serif text-xl font-bold text-roam-ink">{candidate.name}</h3>
                {isSelected && (
                  <span className="bg-roam-green text-white text-[10px] font-mono px-2 py-1 uppercase tracking-wider">
                    Selected
                  </span>
                )}
              </div>
              
              {candidate.state && (
                <p className="text-sm text-roam-ink-light mb-4">{candidate.state}</p>
              )}

              <div className="space-y-3 mb-6">
                {candidate.travel_time_hours > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-roam-ink-light font-mono text-xs">Travel Time</span>
                    <span className="font-medium">{candidate.travel_time_hours}h</span>
                  </div>
                )}
                {candidate.estimated_total_cost > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-roam-ink-light font-mono text-xs">Est. Cost</span>
                    <span className="font-medium">₹{candidate.estimated_total_cost.toLocaleString('en-IN')}</span>
                  </div>
                )}
              </div>

              <div className="border-t border-roam-gray border-opacity-50 pt-4">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-roam-ink-light font-mono text-xs">Match Score</span>
                  <span className="font-bold text-roam-green">{Math.round(candidate.overall_score * 100)}%</span>
                </div>
                <div className="w-full bg-roam-beige h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-roam-green h-full" 
                    style={{ width: `${Math.min(candidate.overall_score * 100, 100)}%` }}
                  ></div>
                </div>
              </div>

              {isRejected && (
                <div className="mt-4 p-3 bg-red-50 text-red-800 text-xs border border-red-100 italic">
                  "{candidate.rejected_reason}"
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
