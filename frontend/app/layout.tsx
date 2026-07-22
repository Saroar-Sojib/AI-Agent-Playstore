import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import BackgroundGlow from "@/components/BackgroundGlow";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AgentHub — AI Agent Catalog",
  description: "Browse AI agent personas, sign up per agent, and chat.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      {/* suppressHydrationWarning: extensions like Grammarly inject
          data-gr-* attributes onto <body> before React hydrates — harmless
          mismatch, not something our code causes or can prevent. */}
      <body className="min-h-full flex flex-col" suppressHydrationWarning>
        <BackgroundGlow />
        {children}
      </body>
    </html>
  );
}
