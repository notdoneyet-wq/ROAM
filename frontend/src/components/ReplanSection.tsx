'use client';

import { useState } from 'react';

interface ReplanSectionProps {
  onReplan: (message: string) => void;
  isLoading: boolean;
}

export default function ReplanSection({ onReplan, isLoading }: ReplanSectionProps) {
  const [input, setInput] = useState('');

  const handleQuickAction = (action: string) => {
    onReplan(action);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onReplan(input);
      setInput('');
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto my-16 bg-roam-beige p-8 border-2 border-roam-ink border-dashed">
      <div className="text-center mb-8">
        <h2 className="font-serif text-3xl text-roam-ink">Adapt Your Trip</h2>
        <p className="font-mono text-xs text-roam-ink-light mt-2 uppercase tracking-widest">Adjust parameters</p>
      </div>

      <div className="flex flex-wrap justify-center gap-3 mb-8">
        <button 
          onClick={() => handleQuickAction("Make it cheaper")}
          disabled={isLoading}
          className="px-4 py-2 bg-white text-sm border border-roam-gray hover:border-roam-ink transition-colors disabled:opacity-50"
        >
          Make it cheaper
        </button>
        <button 
          onClick={() => handleQuickAction("Change pace to more relaxed")}
          disabled={isLoading}
          className="px-4 py-2 bg-white text-sm border border-roam-gray hover:border-roam-ink transition-colors disabled:opacity-50"
        >
          More relaxed pace
        </button>
        <button 
          onClick={() => handleQuickAction("Add more local food experiences")}
          disabled={isLoading}
          className="px-4 py-2 bg-white text-sm border border-roam-gray hover:border-roam-ink transition-colors disabled:opacity-50"
        >
          Focus on food
        </button>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-4 max-w-2xl mx-auto">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="E.g., I want to stay for 2 more days..."
          className="flex-1 bg-white p-3 border border-roam-gray focus:border-roam-ink outline-none font-sans"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="bg-roam-ink text-white px-6 py-3 font-mono text-sm uppercase tracking-wider hover:bg-roam-ink-light transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Updating...' : 'Update Plan'}
        </button>
      </form>
    </div>
  );
}
