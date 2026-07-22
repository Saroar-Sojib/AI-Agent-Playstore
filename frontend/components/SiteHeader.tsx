import Link from "next/link";
import Logo from "./Logo";

export default function SiteHeader({
  right,
}: {
  right?: React.ReactNode;
}) {
  return (
    <header className="sticky top-0 z-10 border-b border-[var(--border-subtle)] bg-[var(--background)]/80 backdrop-blur-md">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2">
          <Logo />
          <span className="text-base font-bold tracking-tight text-neutral-900 dark:text-neutral-50">
            Agent<span className="brand-gradient-text">Hub</span>
          </span>
        </Link>
        {right}
      </div>
    </header>
  );
}
