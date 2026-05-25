'use client';

export default function WalletHeader() {
  return (
    <div className="flex items-center justify-center px-4 py-4 bg-white border-b border-gray-200 relative">
      <button className="absolute left-4 p-0" aria-label="Go back">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M15 18L9 12L15 6"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
      <h1 className="text-lg font-semibold text-black">My Wallet</h1>
    </div>
  );
}
