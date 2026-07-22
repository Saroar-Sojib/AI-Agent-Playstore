// Soft, fixed decorative glow behind all pages — ties the plain background
// to the violet/indigo brand gradient used in the logo/buttons, without
// competing with foreground content (fixed, blurred, low opacity, ignores
// pointer events).
export default function BackgroundGlow() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
    >
      <div
        className="absolute -left-32 -top-40 h-[28rem] w-[28rem] rounded-full opacity-25 blur-3xl dark:opacity-20"
        style={{
          background:
            "radial-gradient(circle, var(--brand-from) 0%, transparent 70%)",
        }}
      />
      <div
        className="absolute -right-24 top-1/3 h-[24rem] w-[24rem] rounded-full opacity-20 blur-3xl dark:opacity-15"
        style={{
          background:
            "radial-gradient(circle, var(--brand-to) 0%, transparent 70%)",
        }}
      />
      <div
        className="absolute bottom-[-10rem] left-1/4 h-[22rem] w-[22rem] rounded-full opacity-15 blur-3xl dark:opacity-10"
        style={{
          background:
            "radial-gradient(circle, var(--brand-from) 0%, transparent 70%)",
        }}
      />
    </div>
  );
}
