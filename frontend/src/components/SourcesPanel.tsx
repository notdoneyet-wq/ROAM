'use client';

import { useState } from 'react';
import { Evidence } from '@/lib/types';

interface SourcesPanelProps {
  evidence: Evidence[];
}

export default function SourcesPanel({ evidence }: SourcesPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!evidence || evidence.length === 0) return null;

  const averageConfidence = Math.round(
    evidence.reduce((acc, curr) => acc + (curr.confidence || 0.9), 0) / evidence.length * 100
  );

  return (
    <div className="w-full max-w-4xl mx-auto my-12 bg-roam-ink text-roam-ivory p-6">
      <div 
        className="flex justify-between items-center cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-3">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-roam-gray">
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path>
          </svg>
          <h3 className="font-serif text-xl tracking-wide">Sources & Evidence</h3>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 text-xs font-mono">
            <span className="text-roam-gray">Grounding Confidence:</span>
            <span className="text-roam-green-light font-bold">{averageConfidence}%</span>
          </div>
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="20" height="20" 
            viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
            className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`}
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </div>

      {isOpen && (
        <div className="mt-6 pt-6 border-t border-roam-gray border-opacity-30 space-y-4">
          {evidence.map((item, idx) => (
            <div key={idx} className="bg-roam-ink-light p-4 text-sm border-l-2 border-roam-terracotta">
              <div className="flex justify-between items-start mb-2">
                <span className="font-mono text-xs uppercase tracking-wider text-roam-gold">{item.source_type}</span>
                <span className="font-mono text-xs text-roam-gray">{Math.round((item.confidence || 0.9) * 100)}% Match</span>
              </div>
              <p className="text-roam-ivory-dark font-sans opacity-90">"{item.data || item.source}"</p>
              {item.url && (
                <a href={item.url} target="_blank" rel="noopener noreferrer" className="inline-block mt-3 text-xs text-roam-blue hover:underline font-mono">
                  [View Source]
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
