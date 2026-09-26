export default function Header() {
  return (
    <header className="flex flex-col items-center justify-center py-12 border-b border-roam-gray border-opacity-30">
      <div className="flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-roam-terracotta">
          <circle cx="12" cy="12" r="10"/>
          <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
        </svg>
        <h1 className="font-serif text-4xl tracking-widest text-roam-ink font-semibold">ROAM</h1>
      </div>
      <p className="mt-4 text-roam-ink-light tracking-[0.2em] text-xs uppercase font-medium">Plan less. Explore more.</p>
    </header>
  );
}
