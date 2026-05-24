'use client';

import IDCard from './components/IDCard';
import SocialChannels from './components/SocialChannels';
import RewardCard from './components/RewardCard';
import { ambassadorProfile, socialChannels, ambassadorRewards } from './mock-data';

export default function AmbassadorMyPage() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-pink-400 via-purple-500 to-blue-600 overflow-x-hidden">
      {/* Close button */}
      <button className="absolute top-4 right-4 text-gray-600 text-2xl z-10">
        ×
      </button>

      {/* Main Container */}
      <div className="max-w-[430px] mx-auto">
        {/* Hero Section with gradient background */}
        <div className="px-4 pt-8 pb-12">
          {/* ID Card */}
          <div className="mb-6">
            <IDCard profile={ambassadorProfile} />
          </div>

          {/* StyleKorean text */}
          <div className="text-center text-white mb-4">
            <div className="text-sm font-medium">StyleKorean</div>
          </div>

          {/* CTA Text */}
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

        {/* White Content Section */}
        <div className="bg-white rounded-t-3xl">
          {/* Welcome Section */}
          <div className="px-6 py-8 text-center">
            <h2 className="text-lg font-bold mb-3">
              WELCOME TO<br />
              STYLEKOREAN AMBASSADOR PROGRAM!
            </h2>
            <p className="text-xs text-gray-600 leading-relaxed">
              StyleKorean, the leading K-beauty channel loved worldwide, invites you to join our community!<br />
              Start your journey to becoming a global K-beauty leader with exclusive perks and exciting opportunities!
            </p>
          </div>

          {/* Social Channels */}
          <SocialChannels channels={socialChannels} />

          {/* Ambassador Rewards */}
          <div className="px-6 py-8 text-center">
            <h3 className="text-sm font-bold mb-6">
              AMBASSADOR REWARDS
            </h3>

            <div className="flex justify-center gap-4 mb-8">
              {ambassadorRewards.map((reward, index) => (
                <RewardCard key={index} reward={reward} index={index} />
              ))}
            </div>

            {/* Join Now Button */}
            <button className="w-full bg-gradient-to-r from-purple-600 to-purple-500 text-white font-bold py-4 rounded-lg text-sm hover:opacity-90 transition-opacity">
              JOIN NOW
            </button>
          </div>

          {/* Follow Section */}
          <div className="px-6 py-8 text-center">
            <h3 className="text-sm font-medium mb-4">
              Follow us the Latest Updates!
            </h3>

            <div className="flex justify-center gap-6 pb-8">
              {/* Instagram */}
              <a href="#" className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400">
                <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                  </svg>
                </div>
              </a>

              {/* YouTube */}
              <a href="#" className="flex items-center justify-center w-10 h-10 rounded-full bg-red-600">
                <div className="w-0 h-0 border-t-[5px] border-t-transparent border-l-[8px] border-l-white border-b-[5px] border-b-transparent ml-1"></div>
              </a>

              {/* TikTok */}
              <a href="#" className="flex items-center justify-center w-10 h-10 rounded-full bg-black relative">
                <div className="text-cyan-400 text-xl font-bold" style={{ textShadow: '1px 1px 0 #fe2c55' }}>
                  ♪
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
