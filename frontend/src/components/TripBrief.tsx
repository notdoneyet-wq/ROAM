import { ExtractedConstraints } from '@/lib/types';
import ConstraintBadge from './ConstraintBadge';

interface TripBriefProps {
  constraints: ExtractedConstraints;
}

export default function TripBrief({ constraints }: TripBriefProps) {
  return (
    <div className="w-full max-w-4xl mx-auto my-12 bg-roam-ivory border-2 border-roam-ink p-8 shadow-[8px_8px_0px_0px_rgba(26,26,46,1)]">
      <div className="flex justify-between items-start mb-8 border-b-2 border-roam-ink pb-4">
        <div>
          <h2 className="font-serif text-3xl font-bold uppercase tracking-wide text-roam-ink">Trip Brief</h2>
          <p className="font-mono text-sm text-roam-ink-light mt-1">EXTRACTED PARAMETERS</p>
        </div>
        <div className="text-right">
          <div className="inline-block border-2 border-roam-terracotta text-roam-terracotta font-mono font-bold px-3 py-1 text-sm transform -rotate-2">
            APPROVED
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {constraints.origin && (
          <ConstraintBadge label="Origin" value={constraints.origin} isHard={true} />
        )}
        {constraints.travellers && (
          <ConstraintBadge label="Travelers" value={constraints.travellers.toString()} isHard={true} />
        )}
        {constraints.duration_days && (
          <ConstraintBadge label="Duration" value={`${constraints.duration_days} days`} isHard={true} />
        )}
        {constraints.budget_inr && (
          <ConstraintBadge label="Budget" value={`₹${constraints.budget_inr.toLocaleString('en-IN')}`} isHard={true} />
        )}
        {constraints.pace && (
          <ConstraintBadge label="Pace" value={constraints.pace} />
        )}
      </div>

      {constraints.interests && constraints.interests.length > 0 && (
        <div className="mt-6">
          <p className="font-mono text-xs uppercase tracking-wider text-roam-ink-light mb-2">Interests</p>
          <div className="flex flex-wrap gap-2">
            {constraints.interests.map((interest, i) => (
              <span key={i} className="px-3 py-1 bg-roam-beige text-roam-ink text-sm rounded-sm">
                {interest}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
