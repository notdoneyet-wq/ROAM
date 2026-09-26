interface ConstraintBadgeProps {
  label: string;
  value: string;
  isHard?: boolean;
}

export default function ConstraintBadge({ label, value, isHard = false }: ConstraintBadgeProps) {
  return (
    <div className={`flex flex-col p-3 rounded-md border ${isHard ? 'border-roam-green bg-roam-ivory' : 'border-dashed border-roam-gray bg-roam-ivory-dark'}`}>
      <div className="flex items-center gap-1 mb-1">
        {isHard ? (
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-roam-green">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-roam-gold">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
          </svg>
        )}
        <span className="text-[10px] uppercase tracking-wider font-mono text-roam-ink-light">{label}</span>
      </div>
      <span className="text-sm font-medium text-roam-ink truncate" title={value}>{value}</span>
    </div>
  );
}
