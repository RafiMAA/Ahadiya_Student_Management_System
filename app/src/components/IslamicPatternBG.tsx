export default function IslamicPatternBG({ className = '' }: { className?: string }) {
  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      <svg width="100%" height="100%" className="opacity-10">
        <defs>
          <pattern id="islamic-star" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">
            <rect x="0" y="0" width="80" height="80" fill="none" />
            <polygon
              points="40,5 45,30 70,25 50,40 70,55 45,50 40,75 35,50 10,55 30,40 10,25 35,30"
              fill="none"
              stroke="currentColor"
              strokeWidth="1"
            />
            <rect x="25" y="25" width="30" height="30" fill="none" stroke="currentColor" strokeWidth="0.5" transform="rotate(45 40 40)" />
            <circle cx="40" cy="40" r="8" fill="none" stroke="currentColor" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#islamic-star)" />
      </svg>
    </div>
  );
}
