'use client';

import { Reward } from '../types';

interface RewardsSectionProps {
  rewards: Reward[];
}

export default function RewardsSection({ rewards }: RewardsSectionProps) {
  return (
    <div className="bg-white px-6 py-8 text-center">
      <h3 className="text-sm font-bold mb-6">
        AMBASSADOR REWARDS
      </h3>

      <div className="flex justify-center gap-4 mb-8">
        {/* Monthly Product Highlights */}
        <div className="flex flex-col items-center flex-1 max-w-[100px]">
          <div className="w-16 h-16 bg-gradient-to-br from-pink-300 to-purple-400 rounded-2xl flex items-center justify-center mb-2 relative">
            <div className="text-3xl">💅</div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-pink-400 rounded-full"></div>
          </div>
          <h4 className="text-[10px] font-bold mb-1 leading-tight">
            Monthly Product Highlights
          </h4>
          <p className="text-[8px] text-gray-600 leading-tight">
            Get exclusive access to the latest beauty trends via our official channel.
          </p>
        </div>

        {/* Free Products */}
        <div className="flex flex-col items-center flex-1 max-w-[100px]">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-300 to-purple-500 rounded-2xl flex items-center justify-center mb-2 relative">
            <div className="text-3xl">💜</div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-purple-400 rounded-full"></div>
          </div>
          <h4 className="text-[10px] font-bold mb-1 leading-tight">
            Free Products to Try
          </h4>
          <p className="text-[8px] text-gray-600 leading-tight">
            Get access to our newest trending K-beauty products.
          </p>
        </div>

        {/* Brand Collaborations */}
        <div className="flex flex-col items-center flex-1 max-w-[100px]">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-300 to-purple-400 rounded-2xl flex items-center justify-center mb-2 relative">
            <div className="text-3xl">🤝</div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-blue-300 rounded-full"></div>
          </div>
          <h4 className="text-[10px] font-bold mb-1 leading-tight">
            Exciting Brand Collaborations
          </h4>
          <p className="text-[8px] text-gray-600 leading-tight">
            Get a chance to collaborate with trending K-beauty brands exclusively.
          </p>
        </div>
      </div>

      {/* Join Now Button */}
      <button className="w-full bg-gradient-to-r from-purple-600 to-purple-500 text-white font-bold py-4 rounded-lg text-sm hover:opacity-90 transition-opacity">
        JOIN NOW
      </button>
    </div>
  );
}
