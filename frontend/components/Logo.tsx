export default function Logo({ size = 28 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="agenthub-logo-grad" x1="0" y1="0" x2="32" y2="32">
          <stop offset="0" stopColor="#8b5cf6" />
          <stop offset="1" stopColor="#4f46e5" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="9" fill="url(#agenthub-logo-grad)" />
      <circle cx="16" cy="16" r="3.4" fill="white" />
      <circle cx="8" cy="9" r="2.2" fill="white" fillOpacity="0.9" />
      <circle cx="24" cy="9" r="2.2" fill="white" fillOpacity="0.9" />
      <circle cx="8" cy="23" r="2.2" fill="white" fillOpacity="0.9" />
      <circle cx="24" cy="23" r="2.2" fill="white" fillOpacity="0.9" />
      <path
        d="M13.6 14 9.6 10.4M18.4 14l4-3.6M13.6 18 9.6 21.6M18.4 18l4 3.6"
        stroke="white"
        strokeOpacity="0.85"
        strokeWidth="1.4"
        strokeLinecap="round"
      />
    </svg>
  );
}
