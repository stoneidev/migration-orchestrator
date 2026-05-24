'use client';

import { AmbassadorReward } from '../types';

interface RewardCardProps {
  reward: AmbassadorReward;
  index: number;
}

export default function RewardCard({ reward, index }: RewardCardProps) {
  const getGradient = (idx: number) => {
    if (idx === 0) return 'from-pink-300 to-purple-400';
    if (idx === 1) return 'from-purple-300 to-purple-500';
    return 'from-blue-300 to-purple-400';
  };

  return (
    <div className="flex flex-col items-center flex-1 max-w-[100px]">
      <div className={`w-16 h-16 bg-gradient-to-br ${getGradient(index)} rounded-2xl flex items-center justify-center mb-2 relative shadow-lg`}>
        <div className="text-3xl">{reward.icon}</div>
        <div className={`absolute -top-1 -right-1 w-4 h-4 rounded-full shadow-md ${
          index === 0 ? 'bg-pink-400' :
          index === 1 ? 'bg-purple-400' :
          'bg-blue-300'
        }`}></div>
      </div>
      <h4 className="text-[10px] font-bold mb-1 leading-tight text-center">
        {reward.title}
      </h4>
      <p className="text-[8px] text-gray-600 leading-tight text-center">
        {reward.description}
      </p>
    </div>
  );
}
