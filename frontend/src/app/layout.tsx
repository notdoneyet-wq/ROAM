import type { Metadata } from "next";
import { Playfair_Display, DM_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const playfair = Playfair_Display({ subsets: ["latin"], variable: '--font-playfair' });
const dmSans = DM_Sans({ subsets: ["latin"], variable: '--font-dmsans' });
const ibmPlexMono = IBM_Plex_Mono({ weight: ["400", "500", "600"], subsets: ["latin"], variable: '--font-ibm-plex-mono' });

export const metadata: Metadata = {
  title: "ROAM AI Travel Agent",
  description: "Plan less. Explore more.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${playfair.variable} ${dmSans.variable} ${ibmPlexMono.variable} font-sans bg-roam-ivory text-roam-ink min-h-screen antialiased selection:bg-roam-green selection:text-white`}>
        <div className="fixed inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIj48cGF0aCBkPSJNMCAwaDQwMHY0MDBIMHoiIGZpbGw9Im5vbmUiLz48cGF0aCBkPSJNMjAwIDIwMGMwIDEwMCAxMDAgMTAwIDEwMCAyMDAiIHN0cm9rZT0icmdiYSgyMDAsIDIwMCwgMjAwLCAwLjEpIiBmaWxsPSJub25lIi8+PC9zdmc+')] opacity-20 pointer-events-none z-0"></div>
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  );
}
