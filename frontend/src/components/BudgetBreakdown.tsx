import { BudgetBreakdown as BudgetBreakdownType } from '@/lib/types';

interface BudgetBreakdownProps {
  budget: BudgetBreakdownType;
}

export default function BudgetBreakdown({ budget }: BudgetBreakdownProps) {
  const categories: [string, number][] = [
    ['Transport', budget.transport || 0],
    ['Accommodation', budget.accommodation || 0],
    ['Food', budget.food || 0],
    ['Activities', budget.activities || 0],
    ['Local Transport', budget.local_transport || 0],
    ['Emergency Buffer', budget.emergency_buffer || 0],
    ['Miscellaneous', budget.miscellaneous || 0],
  ];

  const total = budget.total || 1;
  const maxAmount = Math.max(...categories.map(([_, amount]) => amount), 1);
  const isUnder = budget.status !== 'over_budget';

  return (
    <div className="w-full max-w-4xl mx-auto my-16 bg-white p-8 border border-roam-gray">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 pb-6 border-b border-roam-gray border-opacity-30">
        <div>
          <h2 className="font-serif text-3xl text-roam-ink">Financial Ledger</h2>
          <p className="font-mono text-sm text-roam-ink-light mt-1">ESTIMATED EXPENDITURE</p>
        </div>
        
        <div className="mt-4 md:mt-0 text-right">
          <div className="text-4xl font-serif font-bold text-roam-ink">₹{budget.total.toLocaleString('en-IN')}</div>
          <div className="flex items-center justify-end gap-2 mt-2">
            {isUnder ? (
              <span className="text-xs font-mono bg-roam-green bg-opacity-10 text-roam-green px-2 py-1 uppercase tracking-wider">
                Under Budget ✓
              </span>
            ) : (
              <span className="text-xs font-mono bg-roam-terracotta bg-opacity-10 text-roam-terracotta px-2 py-1 uppercase tracking-wider">
                Over Budget ⚠
              </span>
            )}
            {budget.savings !== undefined && budget.savings > 0 && (
              <span className="text-xs font-mono text-roam-ink-light">
                (₹{budget.savings.toLocaleString('en-IN')} remaining)
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {categories.map(([category, amount], idx) => {
          const percentage = Math.round((amount / total) * 100);
          const barWidth = `${Math.max((amount / maxAmount) * 100, 2)}%`;
          
          return (
            <div key={idx}>
              <div className="flex justify-between items-end mb-2">
                <span className="font-medium text-roam-ink capitalize">{category}</span>
                <div className="text-right">
                  <span className="font-mono text-sm mr-3 text-roam-ink-light">{percentage}%</span>
                  <span className="font-mono font-bold">₹{amount.toLocaleString('en-IN')}</span>
                </div>
              </div>
              <div className="w-full h-3 bg-roam-ivory-dark rounded-sm overflow-hidden">
                <div 
                  className="h-full bg-roam-gold bg-opacity-80" 
                  style={{ width: barWidth }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      {budget.per_person > 0 && (
        <div className="mt-10 pt-6 border-t border-roam-gray border-dashed flex justify-between items-center text-sm font-mono">
          <span className="text-roam-ink-light uppercase tracking-widest">Cost Per Person</span>
          <span className="font-bold text-roam-ink">₹{budget.per_person.toLocaleString('en-IN')}</span>
        </div>
      )}
    </div>
  );
}
