export default function Footer() {
  return (
    <footer className="py-12 mt-24 border-t border-roam-gray border-opacity-30 text-center">
      <p className="font-mono text-xs text-roam-ink-light opacity-70">
        © {new Date().getFullYear()} ROAM AI Travel Agent. Hackathon Project.
      </p>
    </footer>
  );
}
