import { Itinerary as ItineraryType } from '@/lib/types';
import DayCard from './DayCard';

interface ItineraryProps {
  itinerary: ItineraryType;
  origin?: string;
}

export default function Itinerary({ itinerary, origin = "ORIGIN" }: ItineraryProps) {
  return (
    <div className="w-full max-w-4xl mx-auto my-16">
      <div className="mb-16 text-center">
        <h2 className="font-serif text-4xl text-roam-ink mb-4">Expedition Route</h2>
        
        <div className="flex items-center justify-center gap-4 text-sm font-mono text-roam-ink-light mt-6">
          <span className="font-bold text-roam-ink uppercase bg-white border border-roam-gray px-3 py-1">{origin}</span>
          
          <div className="flex-1 max-w-[100px] h-[1px] bg-roam-gray relative">
            <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-roam-gray">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
            </div>
          </div>
          
          <span className="font-bold text-roam-green uppercase bg-white border border-roam-green px-3 py-1 shadow-[2px_2px_0px_0px_rgba(27,67,50,1)]">
            {itinerary.destination}
          </span>
        </div>
      </div>

      <div className="mt-12">
        {itinerary.days.map((day) => (
          <DayCard key={day.day_number} day={day} />
        ))}
      </div>
    </div>
  );
}
