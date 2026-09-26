'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import TripInput from '@/components/TripInput';
import TripBrief from '@/components/TripBrief';
import ResearchStatus from '@/components/ResearchStatus';
import DestinationComparison from '@/components/DestinationComparison';
import Itinerary from '@/components/Itinerary';
import BudgetBreakdown from '@/components/BudgetBreakdown';
import SourcesPanel from '@/components/SourcesPanel';
import ReplanSection from '@/components/ReplanSection';
import SecurityDemo from '@/components/SecurityDemo';
import EvaluationDashboard from '@/components/EvaluationDashboard';
import LoadingSpinner from '@/components/LoadingSpinner';
import { planTrip, replanTrip } from '@/lib/api';
import { PlanResponse, ReplanResponse } from '@/lib/types';
import { motion, AnimatePresence } from 'framer-motion';

type AppState = 'input' | 'planning' | 'results' | 'replanning';

export default function Home() {
  const [appState, setAppState] = useState<AppState>('input');
  const [planResponse, setPlanResponse] = useState<PlanResponse | null>(null);
  const [replanResponse, setReplanResponse] = useState<ReplanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePlanTrip = async (message: string) => {
    setAppState('planning');
    setError(null);
    try {
      const response = await planTrip(message);
      setPlanResponse(response);
      setAppState('results');
    } catch (err: any) {
      setError(err?.message || "Failed to connect to ROAM agent. Please ensure backend is running.");
      setAppState('input');
    }
  };

  const handleReplanTrip = async (message: string) => {
    if (!planResponse?.session_id) return;
    
    setAppState('replanning');
    setError(null);
    try {
      const response = await replanTrip(planResponse.session_id, message);
      setReplanResponse(response);
      
      // Merge new itinerary into current view
      if (planResponse && response.replan_result?.new_itinerary) {
        setPlanResponse({
          ...planResponse,
          itinerary: response.replan_result.new_itinerary
        });
      }
      setAppState('results');
    } catch (err: any) {
      setError(err?.message || "Failed to update trip plan.");
      setAppState('results');
    }
  };

  const selectedDestination = planResponse?.candidates?.find(c => c.selected);

  return (
    <div className="min-h-screen flex flex-col bg-roam-ivory text-roam-ink">
      <Header />
      
      <main className="flex-1 w-full px-4 sm:px-6 lg:px-8 py-8 overflow-x-hidden">
        {error && (
          <div className="w-full max-w-3xl mx-auto bg-red-50 border-2 border-red-200 text-red-800 p-4 mb-8 flex justify-between items-center">
            <span className="font-mono text-sm">{error}</span>
            <button onClick={() => setError(null)} className="font-bold">×</button>
          </div>
        )}

        <AnimatePresence mode="wait">
          {appState === 'input' && (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <TripInput onSubmit={handlePlanTrip} isLoading={false} />
            </motion.div>
          )}

          {(appState === 'planning' || appState === 'replanning') && (
            <motion.div
              key="planning"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="py-20"
            >
              <div className="text-center mb-8">
                <h2 className="font-serif text-3xl text-roam-ink mb-2">
                  {appState === 'planning' ? 'Consulting the Archives...' : 'Recalculating Routes...'}
                </h2>
                <p className="font-mono text-sm text-roam-terracotta uppercase tracking-widest">
                  ROAM AI is at work
                </p>
              </div>
              <LoadingSpinner />
              {planResponse && appState === 'replanning' && (
                <div className="mt-8 text-center font-mono text-sm text-roam-ink-light opacity-70">
                  Adapting your parameters based on new constraints...
                </div>
              )}
            </motion.div>
          )}

          {appState === 'results' && planResponse && (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-16"
            >
              {/* If we replanned, show change summary */}
              {replanResponse?.replan_result?.changes && (
                <div className="w-full max-w-4xl mx-auto bg-roam-green bg-opacity-10 border border-roam-green p-6 mb-8">
                  <h3 className="font-mono font-bold text-roam-green uppercase tracking-wide mb-4 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M2.5 2v6h6M21.5 22v-6h-6M22 11.5A10 10 0 0 0 3.2 7.2M2 12.5a10 10 0 0 0 18.8 4.2"/>
                    </svg>
                    Plan Updated
                  </h3>
                  <div className="space-y-2">
                    {replanResponse.replan_result.changes.map((change, idx) => (
                      <div key={idx} className="flex items-center text-sm font-sans gap-2">
                        <span className="font-mono text-xs uppercase bg-white px-2 py-0.5 border border-roam-gray">{change.field}</span>
                        <span className="text-roam-ink-light line-through">{change.old_value}</span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-roam-green mx-1">
                          <line x1="5" y1="12" x2="19" y2="12"></line>
                          <polyline points="12 5 19 12 12 19"></polyline>
                        </svg>
                        <span className="font-bold text-roam-ink">{change.new_value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <TripBrief constraints={planResponse.constraints} />
              
              {!replanResponse && (
                <>
                  <ResearchStatus steps={planResponse.planning_steps} />
                  <DestinationComparison 
                    candidates={planResponse.candidates} 
                    selectedName={selectedDestination?.name} 
                  />
                </>
              )}

              {planResponse.itinerary && (
                <>
                  <Itinerary 
                    itinerary={planResponse.itinerary} 
                    origin={planResponse.constraints?.origin || 'Delhi'} 
                  />
                  <BudgetBreakdown budget={planResponse.itinerary.budget} />
                  <SourcesPanel evidence={planResponse.itinerary.evidence} />
                </>
              )}

              <ReplanSection onReplan={handleReplanTrip} isLoading={false} />
              
              <div className="w-full max-w-5xl mx-auto border-t border-roam-gray border-dashed pt-16 mt-24">
                <div className="text-center mb-12">
                  <h2 className="font-serif text-3xl text-roam-ink opacity-50">System Diagnostics</h2>
                  <p className="font-mono text-xs text-roam-ink-light mt-2 uppercase tracking-widest opacity-50">HACKATHON REVIEW PANEL</p>
                </div>
                <SecurityDemo />
                <EvaluationDashboard />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <Footer />
    </div>
  );
}
