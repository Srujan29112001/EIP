import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Space_Grotesk } from "next/font/google";
import { CursorGlow } from "@/components/fx/cursor-glow";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space-grotesk" });
const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const jetbrains = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains" });

export const metadata: Metadata = {
  title: "EIP — The Money Intelligence OS",
  description:
    "A transparent board of 91 specialist AI agents that researches your idea, stock, or salary with live data, argues about it, audits your biases, and hands you a weighted, sourced decision.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en"
      className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrains.variable}`}>
      <body className="texture min-h-screen bg-ink antialiased">
        <div className="aurora" aria-hidden />
        <CursorGlow />
        {children}
      </body>
    </html>
  );
}
