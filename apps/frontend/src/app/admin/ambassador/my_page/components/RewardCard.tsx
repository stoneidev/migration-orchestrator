'use client';

import { AmbassadorReward } from '../types';

interface RewardCardProps {
  reward: AmbassadorReward;
  index: number;
}

export default function RewardCard({ reward, index }: RewardCardProps) {
  const getGradient = (idx: number) => {
    if (idx === 0) return 'from-pink-300 via-purple-300 to-purple-200';
    if (idx === 1) return 'from-purple-300 via-purple-200 to-blue-200';
    return 'from-blue-200 via-purple-200 to-pink-200';
  };

  return (
    <div className="flex flex-col items-center flex-1 text-center">
      <div className={`w-[58px] h-[58px] bg-gradient-to-br ${getGradient(index)} rounded-2xl flex items-center justify-center mb-2.5 shadow-sm`}>
        <div className="text-[28px]">{reward.icon}</div>
      </div>
      <h4 className="text-[10px] font-bold mb-1.5 leading-tight px-0.5">
        {reward.title}
      </h4>
      <p className="text-[9px] text-gray-600 leading-snug px-0.5">
        {reward.description}
      </p>
    </div>
  );
}
