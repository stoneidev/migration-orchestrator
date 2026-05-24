'use client';

export default function FooterSection() {
  return (
    <div className="bg-white px-6 py-8 text-center">
      <h3 className="text-sm font-medium mb-4">
        Follow us the Latest Updates!
      </h3>

      <div className="flex justify-center gap-6">
        {/* Instagram */}
        <a href="#" className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400">
          <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
            <div className="w-5 h-5 border-2 border-black rounded-lg relative">
              <div className="absolute top-0.5 right-0.5 w-1 h-1 bg-black rounded-full"></div>
            </div>
          </div>
        </a>

        {/* YouTube */}
        <a href="#" className="flex items-center justify-center w-10 h-10 rounded-full bg-red-600">
          <div className="w-0 h-0 border-t-[5px] border-t-transparent border-l-[8px] border-l-white border-b-[5px] border-b-transparent ml-1"></div>
        </a>

        {/* TikTok */}
        <a href="#" className="flex items-center justify-center w-10 h-10 rounded-full bg-black relative">
          <div className="absolute text-cyan-400 text-xl font-bold" style={{ textShadow: '1px 1px 0 #fe2c55' }}>
            ♪
          </div>
        </a>
      </div>
    </div>
  );
}
