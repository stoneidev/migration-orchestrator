'use client';

import IDCard from './components/IDCard';
import SocialChannels from './components/SocialChannels';
import RewardCard from './components/RewardCard';
import { ambassadorProfile, socialChannels, ambassadorRewards } from './mock-data';

export default function AmbassadorMyPage() {
  return (
    <div className="min-h-screen w-full bg-white overflow-x-hidden">
      {/* Main Container */}
      <div className="max-w-[430px] mx-auto">
        {/* Hero Section with gradient background */}
        <div className="relative bg-gradient-to-br from-pink-400 via-purple-500 to-orange-300 px-4 pt-6 pb-8">
          {/* Close button */}
          <button className="absolute top-3 right-3 text-white text-xl font-light z-10 w-8 h-8 flex items-center justify-center">
            ×
          </button>

          {/* ID Card */}
          <div className="mb-5 pt-2">
            <IDCard profile={ambassadorProfile} />
          </div>

          {/* CTA Text */}
          <div className="text-center text-white px-4">
            <div className="text-[10px] mb-0.5 leading-relaxed font-normal tracking-wide">
              GET ACCESS TO EXCLUSIVE PR BOXES
            </div>
            <div className="text-[10px] mb-3 leading-relaxed font-normal tracking-wide">
              & EXCITING BRAND COLLABS!
            </div>
            <div className="text-[22px] font-bold leading-tight tracking-tight">
              JOIN OUR STYLEKOREAN<br />
              AMBASSADOR!
            </div>
          </div>
        </div>

        {/* White Content Section */}
        <div className="bg-white">
          {/* Welcome Section */}
          <div className="px-6 py-7 text-center">
            <h2 className="text-[15px] font-bold mb-3 leading-tight tracking-tight">
              WELCOME TO<br />
              STYLEKOREAN AMBASSADOR PROGRAM!
            </h2>
            <p className="text-[11px] text-gray-700 leading-relaxed">
              As the leading K-beauty channel and innovative,<br />
              StyleKorean Ambassador opens new opportunities.<br />
              Start your journey to becoming a global K-beauty leader<br />
              with exclusive perks and endless collaborations!
            </p>
          </div>

          {/* Social Channels */}
          <SocialChannels channels={socialChannels} />

          {/* Ambassador Rewards */}
          <div className="px-6 py-7 text-center bg-white">
            <h3 className="text-[13px] font-bold mb-5 tracking-tight">
              AMBASSADOR REWARDS
            </h3>

            <div className="flex justify-between gap-3 mb-7">
              {ambassadorRewards.map((reward, index) => (
                <RewardCard key={index} reward={reward} index={index} />
              ))}
            </div>

            {/* Join Now Button */}
            <button className="w-full bg-gradient-to-r from-purple-600 to-purple-500 text-white font-bold py-3.5 rounded-lg text-[13px] shadow-md tracking-wide">
              JOIN NOW
            </button>
          </div>

          {/* Follow Section */}
          <div className="px-6 pb-8 pt-1 text-center bg-white">
            <h3 className="text-[12px] font-semibold mb-4">
              Follow us the Latest Updates!
            </h3>

            <div className="flex justify-center gap-5">
              {/* Instagram */}
              <a href="#" className="flex items-center justify-center w-[46px] h-[46px] rounded-full bg-gradient-to-br from-pink-400 via-pink-500 to-pink-600 shadow-sm">
                <svg className="w-[22px] h-[22px] text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
              </a>

              {/* YouTube */}
              <a href="#" className="flex items-center justify-center w-[46px] h-[46px] rounded-full bg-red-600 shadow-sm">
                <svg className="w-[24px] h-[24px] text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </a>

              {/* TikTok */}
              <a href="#" className="flex items-center justify-center w-[46px] h-[46px] rounded-full bg-black shadow-sm">
                <svg className="w-[20px] h-[20px] text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
