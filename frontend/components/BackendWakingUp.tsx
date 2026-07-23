"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const RETRY_SECONDS = 10;

export default function BackendWakingUp() {
  const router = useRouter();
  const [secondsLeft, setSecondsLeft] = useState(RETRY_SECONDS);

  useEffect(() => {
    const tick = setInterval(() => {
      setSecondsLeft((s) => (s <= 1 ? RETRY_SECONDS : s - 1));
    }, 1000);
    const retry = setInterval(() => router.refresh(), RETRY_SECONDS * 1000);
    return () => {
      clearInterval(tick);
      clearInterval(retry);
    };
  }, [router]);

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-3 px-4 py-24 text-center">
      <div className="brand-gradient-bg flex h-11 w-11 items-center justify-center rounded-2xl text-lg">
        ⏳
      </div>
      <h1 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">
        Waking up the server…
      </h1>
      <p className="max-w-sm text-sm text-neutral-500 dark:text-neutral-400">
        This app runs on free-tier hosting, so the backend goes to sleep when
        idle. It takes up to a minute to start — retrying automatically every{" "}
        {RETRY_SECONDS} seconds (next try in {secondsLeft}s).
      </p>
    </div>
  );
}
