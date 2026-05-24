'use client';

import { AmbassadorProfile } from '../types';

interface IDCardProps {
  profile: AmbassadorProfile;
}

export default function IDCard({ profile }: IDCardProps) {
  return (
    <div className="relative w-48 mx-auto">
      {/* Keychain ring at top */}
      <div className="flex justify-center mb-2">
        <div className="w-8 h-8 bg-gray-400 rounded-full border-4 border-gray-500 relative">
          <div className="absolute -top-1.5 left-1/2 transform -translate-x-1/2 w-6 h-3 bg-gray-500 rounded-t-lg"></div>
        </div>
      </div>

      {/* Keychain beads */}
      <div className="flex justify-center gap-1 mb-3">
        <div className="w-6 h-6 bg-pink-400 rounded-full shadow-md"></div>
        <div className="w-6 h-6 bg-pink-300 rounded-full shadow-md"></div>
        <div className="w-6 h-6 bg-pink-500 rounded-full shadow-md"></div>
      </div>

      {/* ID Card main body */}
      <div className="bg-gradient-to-br from-gray-200 to-gray-300 rounded-t-xl p-3 shadow-xl">
        {/* White card content */}
        <div className="bg-white rounded-lg p-3 shadow-inner relative">
          {/* Logo circle with A */}
          <div className="flex justify-center mb-2">
            <div className="w-12 h-12 bg-pink-500 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-md">
              A
            </div>
          </div>

          {/* Text info - very small font */}
          <div className="text-[9px] leading-tight space-y-0.5 font-mono">
            <div><span className="font-bold">NAME:</span> {profile.name}</div>
            <div><span className="font-bold">COUNTRY:</span> {profile.country}</div>
            <div><span className="font-bold">BIRTH DATE:</span> {profile.birthday}</div>
            <div><span className="font-bold">ID NUMBER:</span> {profile.sns}</div>
          </div>
        </div>
      </div>

      {/* Black AMBASSADOR tag at bottom */}
      <div className="bg-black text-white text-center py-2 text-xs font-bold tracking-wider shadow-lg">
        AMBASSADOR
      </div>
    </div>
  );
}
