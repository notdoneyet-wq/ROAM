import { DayPlan } from '@/lib/types';

interface DayCardProps {
  day: DayPlan;
}

export default function DayCard({ day }: DayCardProps) {
  return (
    <div className="mb-12 relative">
      {/* Day stamp connector */}
      <div className="absolute left-6 top-16 bottom-[-48px] w-0.5 bg-roam-gray bg-opacity-30 hidden md:block"></div>
      
      <div className="flex flex-col md:flex-row gap-6">
        {/* Day Stamp */}
        <div className="relative z-10 md:w-32 flex-shrink-0">
          <div className="inline-flex flex-col items-center justify-center w-16 h-16 rounded-full border-2 border-roam-ink bg-roam-ivory shadow-[2px_2px_0px_0px_rgba(26,26,46,1)]">
            <span className="text-[10px] font-mono tracking-widest font-bold uppercase leading-none">Day</span>
            <span className="text-2xl font-serif font-bold leading-none mt-1">{day.day_number.toString().padStart(2, '0')}</span>
          </div>
        </div>

        {/* Content Card */}
        <div className="flex-1 bg-white border border-roam-gray p-6 sm:p-8 rounded-sm hover:border-roam-green transition-colors">
          <div className="mb-6 border-b border-roam-gray border-opacity-30 pb-4">
            <h3 className="font-serif text-2xl text-roam-ink mb-2">{day.title}</h3>
            <div className="flex items-center gap-2 text-roam-ink-light text-sm font-mono">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              {day.location}
            </div>
          </div>

          <div className="space-y-6">
            {/* Activities */}
            {(day.morning.length > 0 || day.afternoon.length > 0 || day.evening.length > 0) && (
              <div>
                <h4 className="text-xs font-mono uppercase tracking-widest text-roam-terracotta mb-4">Activities</h4>
                <div className="space-y-3">
                  {[...day.morning, ...day.afternoon, ...day.evening].map((activity, idx) => (
                    <div key={idx} className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-roam-ink">{activity.name}</p>
                        <p className="text-xs text-roam-ink-light">{activity.duration_hours}h • {activity.category}</p>
                      </div>
                      <span className="text-sm font-mono">₹{activity.cost_per_person.toLocaleString('en-IN')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Meals */}
            {day.meals.length > 0 && (
              <div>
                <h4 className="text-xs font-mono uppercase tracking-widest text-roam-terracotta mb-4">Provisions</h4>
                <div className="space-y-3 bg-roam-ivory-dark p-4 border border-roam-gray border-dashed">
                  {day.meals.map((meal, idx) => (
                    <div key={idx} className="flex justify-between items-center">
                      <div>
                        <span className="text-xs font-mono font-bold mr-2 uppercase w-16 inline-block">{meal.time_slot}</span>
                        <span className="text-sm text-roam-ink">{meal.name}</span>
                      </div>
                      <span className="text-sm font-mono">₹{meal.cost_per_person.toLocaleString('en-IN')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Accommodation */}
            {day.accommodation && (
              <div>
                <h4 className="text-xs font-mono uppercase tracking-widest text-roam-terracotta mb-4">Lodging</h4>
                <div className="flex justify-between items-center text-sm border-l-2 border-roam-green pl-3 py-1">
                  <span className="font-medium text-roam-ink">{day.accommodation.name}</span>
                  <span className="font-mono">₹{day.accommodation.cost_per_night.toLocaleString('en-IN')}/night</span>
                </div>
              </div>
            )}
          </div>

          <div className="mt-8 pt-4 border-t border-roam-gray border-opacity-30 flex flex-wrap gap-4 justify-between items-center">
            <div className="flex gap-2">
              {day.highlights.map((highlight, idx) => (
                <span key={idx} className="text-[10px] bg-roam-beige px-2 py-1 uppercase tracking-wider text-roam-ink">
                  {highlight}
                </span>
              ))}
            </div>
            <div className="text-sm font-mono">
              <span className="text-roam-ink-light">Day Cost:</span> <span className="font-bold text-roam-ink">₹{day.daily_cost.toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
