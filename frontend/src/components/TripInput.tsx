'use client';

import { useState } from 'react';

const SUGGESTIONS = [
  "Weekend escape from SF",
  "Nature + food in Japan",
  "Budget trip to Mexico",
  "Adventure in Patagonia",
  "Slow travel in Tuscany"
];

interface TripInputProps {
  onSubmit: (message: string) => void;
  isLoading: boolean;
}

export default function TripInput({ onSubmit, isLoading }: TripInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSubmit(input);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto my-16 px-4">
      <div className="text-center mb-8">
        <h2 className="font-serif text-5xl md:text-6xl text-roam-ink mb-4">Where will you go?</h2>
        <p className="font-mono text-roam-terracotta text-sm tracking-widest">
          37.7749° N, 122.4194° W · AWAITING COORDINATES
        </p>
      </div>

      <form onSubmit={handleSubmit} className="relative">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe your ideal trip. Mention your starting point, duration, budget, and who is traveling..."
          className="w-full h-40 p-6 bg-roam-ivory border-2 border-roam-gray focus:border-roam-green outline-none resize-none text-lg font-sans placeholder-roam-gray rounded-sm transition-colors"
          disabled={isLoading}
        />
        <div className="absolute bottom-6 right-6">
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-roam-terracotta hover:bg-roam-terracotta-light text-white px-8 py-3 uppercase tracking-wider text-sm font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Plotting Route...' : 'Plan my trip'}
          </button>
        </div>
      </form>

      <div className="mt-8">
        <p className="font-mono text-xs text-roam-ink-light uppercase tracking-wider mb-4 text-center">Field notes inspiration</p>
        <div className="flex flex-wrap gap-3 justify-center">
          {SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => setInput(suggestion)}
              disabled={isLoading}
              className="text-xs px-4 py-2 border border-roam-gray text-roam-ink-light hover:border-roam-green hover:text-roam-green transition-colors rounded-full"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
