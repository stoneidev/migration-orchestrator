'use client';

import { AmbassadorInfo } from '../types';

interface HeroSectionProps {
  ambassador: AmbassadorInfo;
}

export default function HeroSection({ ambassador }: HeroSectionProps) {
  return (
    <div className="relative w-full px-4 pt-8 pb-12">
      {/* Close button */}
      <button className="absolute top-4 right-4 text-gray-600 text-2xl">
        ×
      </button>

      {/* ID Card */}
      <div className="mx-auto w-48 mb-6">
        <div className="bg-gradient-to-br from-gray-200 to-gray-300 rounded-t-xl p-3 shadow-lg">
          {/* Keychain ring */}
          <div className="flex justify-center mb-2">
            <div className="w-8 h-8 bg-gray-400 rounded-full border-4 border-gray-500 relative">
              <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-6 h-2 bg-gray-500 rounded-t-lg"></div>
            </div>
          </div>

          {/* Keychain attachments */}
          <div className="flex justify-center gap-1 mb-3">
            <div className="w-6 h-6 bg-pink-400 rounded-full"></div>
            <div className="w-6 h-6 bg-pink-300 rounded-full"></div>
            <div className="w-6 h-6 bg-pink-500 rounded-full"></div>
          </div>

          {/* Card content */}
          <div className="bg-white rounded-lg p-3 shadow-inner">
            {/* Logo */}
            <div className="flex justify-center mb-2">
              <div className="w-12 h-12 bg-pink-500 rounded-full flex items-center justify-center text-white text-xl font-bold">
                A
              </div>
            </div>

            {/* Text info */}
            <div className="text-[9px] leading-tight space-y-0.5 font-mono">
              <div><span className="font-bold">NAME:</span> {ambassador.name}</div>
              <div><span className="font-bold">COUNTRY:</span> {ambassador.country}</div>
              <div><span className="font-bold">BIRTH DATE:</span> {ambassador.birthDate}</div>
              <div><span className="font-bold">ID NUMBER:</span> {ambassador.idNumber}</div>
            </div>
          </div>
        </div>

        {/* Black tag */}
        <div className="bg-black text-white text-center py-2 text-xs font-bold tracking-wider">
          AMBASSADOR
        </div>
      </div>

      {/* StyleKorean text */}
      <div className="text-center text-white mb-4">
        <div className="text-sm font-medium">StyleKorean</div>
      </div>

      {/* Main CTA text */}
      <div className="text-center text-white px-6">
        <div className="text-xs mb-2 leading-relaxed">
          GET ACCESS TO EXCLUSIVE PR BOXES<br />
          & EXCITING BRAND COLLABS!
        </div>
        <div className="text-lg font-bold leading-tight">
          JOIN OUR STYLEKOREAN<br />
          AMBASSADOR!
        </div>
      </div>
    </div>
  );
}
