import Link from "next/link";
export function Brand() {
  return (
    <Link href="/" className="brand" aria-label="Outcomia home">
      <svg viewBox="0 0 36 36" fill="none" aria-hidden="true">
        <circle
          cx="17"
          cy="19"
          r="11"
          stroke="currentColor"
          strokeWidth="3.5"
        />
        <path
          d="M19 17 29 7m-7 0h7v7"
          stroke="currentColor"
          strokeWidth="3.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span>Outcomia</span>
    </Link>
  );
}
