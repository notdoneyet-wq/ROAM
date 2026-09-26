import { motion } from 'framer-motion';
import { PlanningStep } from '@/lib/types';

interface ResearchStatusProps {
  steps: PlanningStep[];
}

export default function ResearchStatus({ steps }: ResearchStatusProps) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="w-full max-w-3xl mx-auto my-12 p-8 bg-roam-ivory-dark border border-roam-gray rounded-sm">
      <h3 className="font-serif text-2xl text-roam-ink mb-6 flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-roam-green">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        Field Research Pipeline
      </h3>

      <div className="space-y-6">
        {steps.map((step, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-start gap-4 relative"
          >
            {/* Timeline line */}
            {index < steps.length - 1 && (
              <div className="absolute left-[11px] top-8 bottom-[-24px] w-0.5 bg-roam-gray bg-opacity-50 z-0"></div>
            )}
            
            <div className="relative z-10 mt-1">
              {step.status === 'complete' && (
                <div className="w-6 h-6 rounded-full bg-roam-green flex items-center justify-center text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                </div>
              )}
              {step.status === 'running' && (
                <div className="w-6 h-6 rounded-full border-2 border-roam-terracotta border-t-transparent animate-spin"></div>
              )}
              {step.status === 'pending' && (
                <div className="w-6 h-6 rounded-full bg-roam-gray bg-opacity-30"></div>
              )}
              {step.status === 'error' && (
                <div className="w-6 h-6 rounded-full bg-red-500 flex items-center justify-center text-white">
                  <span className="text-xs font-bold">!</span>
                </div>
              )}
            </div>
            
            <div className="flex-1">
              <p className={`font-medium ${step.status === 'pending' ? 'text-roam-gray' : 'text-roam-ink'}`}>
                {step.label || step.step}
              </p>
              {step.detail && (
                <p className="text-xs text-roam-ink-light font-mono mt-0.5">{step.detail}</p>
              )}
              
              {step.tool_calls && step.tool_calls.length > 0 && (
                <div className="mt-2 space-y-2">
                  {step.tool_calls.map((tool, idx) => (
                    <div key={idx} className="text-xs font-mono bg-white p-2 border border-roam-gray border-opacity-50 rounded">
                      <span className="text-roam-blue font-bold">{tool.tool_name}</span>
                      <span className="text-roam-ink-light ml-2">{tool.result_summary}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
