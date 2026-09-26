'use client';

import { useState } from 'react';
import { runEvaluation } from '@/lib/api';
import { EvaluationResult } from '@/lib/types';

export default function EvaluationDashboard() {
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunEval = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await runEvaluation();
      setResult(response.result);
    } catch {
      setError("Failed to connect to evaluation service. Make sure the backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto my-16 bg-roam-ink p-8 text-roam-ivory">
      <div className="flex justify-between items-center mb-8 border-b border-roam-gray border-opacity-30 pb-4">
        <div>
          <h2 className="font-serif text-2xl tracking-wide">Agent Evaluation</h2>
          <p className="font-mono text-xs text-roam-gray mt-1 uppercase tracking-widest">PERFORMANCE METRICS</p>
        </div>
        <button 
          onClick={handleRunEval}
          disabled={isLoading}
          className="bg-roam-green hover:bg-roam-green-light text-white font-mono text-sm px-4 py-2 transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Running Tests...' : 'Run Evaluation Suite'}
        </button>
      </div>

      {error && (
        <div className="bg-red-900 bg-opacity-30 border border-red-500 text-red-200 p-4 mb-6 text-sm font-mono">
          {error}
        </div>
      )}

      {result ? (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="col-span-1 border border-roam-gray border-opacity-30 p-6 flex flex-col justify-center items-center">
              <span className="text-5xl font-serif font-bold text-roam-gold mb-2">{result.overall_score}%</span>
              <span className="font-mono text-xs uppercase tracking-wider text-roam-gray">Overall Score</span>
            </div>
            <div className="col-span-2 border border-roam-gray border-opacity-30 p-6">
              <h4 className="font-mono text-xs uppercase tracking-wider text-roam-gray mb-4">Category Scores</h4>
              <div className="space-y-4">
                {Object.entries(result.categories || {}).map(([category, score], idx) => {
                  const numScore = Number(score);
                  return (
                    <div key={idx}>
                      <div className="flex justify-between text-sm font-mono mb-1">
                        <span>{category.replace('_', ' ')}</span>
                        <span>{numScore}%</span>
                      </div>
                      <div className="w-full h-1 bg-roam-ink-light overflow-hidden">
                        <div 
                          className={`h-full ${numScore > 80 ? 'bg-roam-green' : numScore > 50 ? 'bg-roam-gold' : 'bg-roam-terracotta'}`}
                          style={{ width: `${numScore}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-mono text-xs uppercase tracking-wider text-roam-gray mb-4">Test Cases</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {result.test_cases.map((test, idx) => (
                <div key={idx} className="bg-roam-ink-light p-3 flex items-start gap-3 border-l-2 border-opacity-50" style={{ borderColor: test.passed ? '#2D6A4F' : '#C17F59' }}>
                  <div className="mt-0.5">
                    {test.passed ? (
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C17F59" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                    )}
                  </div>
                  <div>
                    <div className="flex gap-2 items-center mb-1">
                      <span className="font-mono text-xs font-bold">{test.name}</span>
                      <span className="text-[10px] bg-roam-ink px-1 text-roam-gray uppercase">{test.category}</span>
                    </div>
                    <p className="text-xs text-roam-ivory opacity-80">{test.details}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 border border-roam-gray border-opacity-30 border-dashed">
          <p className="font-mono text-sm text-roam-gray">Click run to evaluate the agent's performance against baseline metrics.</p>
        </div>
      )}
    </div>
  );
}
