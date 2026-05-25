'use client';

export default function ChatButton() {
  return (
    <button className="fixed bottom-24 right-4 bg-pink-400 text-white rounded-full pl-4 pr-5 py-3 shadow-lg flex items-center gap-2 hover:bg-pink-500 transition-colors z-50">
      <span className="text-sm font-medium">Chat with us</span>
      <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z"
            fill="#EC4899"
            stroke="#EC4899"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </button>
  );
}
