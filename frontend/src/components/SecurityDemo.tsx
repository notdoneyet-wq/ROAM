'use client';

import { useState } from 'react';
import { SecurityEvent } from '@/lib/types';
import { runSecurityDemo } from '@/lib/api';

export default function SecurityDemo() {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [isTesting, setIsTesting] = useState(false);

  const simulateAttack = async () => {
    setIsTesting(true);
    try {
      const demoRes = await runSecurityDemo();
      if (demoRes && demoRes.events) {
        setEvents(demoRes.events);
      }
    } catch {
      // Fallback local demo if server not reachable
      const newEvent: SecurityEvent = {
        type: "instruction_override",
        source: "user_input",
        status: "blocked",
        content_snippet: "Ignore system rules...",
        detail: "Blocked instruction override pattern: System prompt protection engaged."
      };
      setEvents(prev => [newEvent, ...prev]);
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto my-12 border border-roam-gray bg-white p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-roam-terracotta">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          <h3 className="font-mono font-bold text-roam-ink uppercase tracking-wide">Security Monitor</h3>
        </div>
        <button 
          onClick={simulateAttack}
          disabled={isTesting}
          className="text-xs font-mono border border-roam-terracotta text-roam-terracotta px-3 py-1 hover:bg-roam-terracotta hover:text-white transition-colors disabled:opacity-50"
        >
          {isTesting ? 'Testing...' : 'Run Security Suite'}
        </button>
      </div>

      <div className="bg-roam-ivory h-48 overflow-y-auto p-4 border-2 border-roam-gray border-dashed font-mono text-sm">
        {events.length === 0 ? (
          <div className="h-full flex items-center justify-center text-roam-ink-light opacity-50">
            System secure. Click "Run Security Suite" to test prompt injection defenses...
          </div>
        ) : (
          <div className="space-y-3">
            {events.map((evt, i) => (
              <div key={i} className="flex flex-col border-l-2 border-roam-terracotta pl-3">
                <div className="flex justify-between items-center text-xs text-roam-ink-light mb-1">
                  <span className="uppercase font-bold">{evt.type}</span>
                  <span className={`px-1 font-bold ${evt.status === 'blocked' ? 'bg-roam-terracotta text-white' : 'bg-roam-gold text-roam-ink'}`}>
                    {evt.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-roam-ink text-xs">{evt.detail}</p>
                <span className="text-[10px] text-roam-gray mt-1">Source: {evt.source}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
