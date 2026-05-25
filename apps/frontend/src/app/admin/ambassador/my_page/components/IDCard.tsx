'use client';

import { AmbassadorProfile } from '../types';

interface IDCardProps {
  profile: AmbassadorProfile;
}

export default function IDCard({ profile }: IDCardProps) {
  return (
    <div className="relative w-36 mx-auto">
      {/* Keychain ring at top */}
      <div className="flex justify-center mb-1">
        <div className="relative">
          <div className="w-9 h-7 bg-gradient-to-b from-gray-300 to-gray-400 rounded-md shadow-md border border-gray-400"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-3 bg-gray-200 rounded-sm"></div>
        </div>
      </div>

      {/* Main card container with right side tag */}
      <div className="relative">
        {/* White card content */}
        <div className="bg-white rounded-md p-3 shadow-2xl border border-gray-100">
          {/* Logo circle with gradient background and white center with A */}
          <div className="flex justify-center mb-3">
            <div className="w-16 h-16 bg-gradient-to-br from-pink-400 via-pink-500 to-pink-600 rounded-full flex items-center justify-center shadow-md p-1">
              <div className="w-full h-full bg-white rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold bg-gradient-to-br from-pink-400 to-pink-600 bg-clip-text text-transparent">A</span>
              </div>
            </div>
          </div>

          {/* Text info */}
          <div className="text-[8.5px] leading-tight space-y-0.5 text-black">
            <div><span className="font-bold">NAME</span> : {profile.name}</div>
            <div><span className="font-bold">COUNTRY</span> : {profile.country}</div>
            <div><span className="font-bold">BIRTH DATE</span> : {profile.birthDate}</div>
            <div><span className="font-bold">SKIN TYPE</span> : {profile.skinType}</div>
          </div>
        </div>

        {/* Vertical AMBASSADOR tag on right side */}
        <div className="absolute -right-0.5 top-0 bottom-0 bg-black text-white text-[8px] font-bold px-1.5 flex items-center justify-center rounded-r-md" style={{ writingMode: 'vertical-rl', letterSpacing: '0.05em' }}>
          AMBASSADOR
        </div>
      </div>
    </div>
  );
}
