'use client';

import { useState } from 'react';
import { mockQuestions } from './mock-data';
import { PeriodFilter, CategoryFilter } from './types';

export default function MyQuestionPage() {
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>('All');
  const [periodFilter, setPeriodFilter] = useState<PeriodFilter>('1 Month');
  const [startDate, setStartDate] = useState('04/25/2026');
  const [endDate, setEndDate] = useState('05/25/2026');

  const handleSearch = () => {
    console.log('Search:', { categoryFilter, periodFilter, startDate, endDate });
  };

  return (
    <div className="min-h-screen bg-white" style={{ maxWidth: '430px', margin: '0 auto' }}>
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-4 border-b border-gray-200">
        <button className="p-2" aria-label="Go back">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 className="text-lg font-semibold text-gray-900">My Question</h1>
        <div className="w-10"></div>
      </header>

      {/* Filter Section */}
      <div className="px-4 pt-6 pb-4">
        {/* Category Dropdown */}
        <div className="mb-4">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg appearance-none bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%23666' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")`,
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'right 16px center',
            }}
          >
            <option value="All">All</option>
            <option value="Beauty">Beauty</option>
            <option value="Food">Food</option>
            <option value="Electronics">Electronics</option>
          </select>
        </div>

        {/* Period Filter Buttons */}
        <div className="flex gap-2 mb-4">
          {(['1 Week', '1 Month', '3 Month', 'This Year'] as PeriodFilter[]).map((period) => (
            <button
              key={period}
              onClick={() => setPeriodFilter(period)}
              className={`flex-1 py-3 text-sm font-medium rounded-lg transition-colors ${
                periodFilter === period
                  ? 'bg-black text-white'
                  : 'bg-white text-gray-700 border border-gray-300'
              }`}
            >
              {period}
            </button>
          ))}
        </div>

        {/* Date Range */}
        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#999" strokeWidth="1.5">
                <rect x="3" y="4" width="14" height="14" rx="2" />
                <path d="M3 8h14M7 2v4M13 2v4" />
              </svg>
            </div>
          </div>
          <span className="text-gray-500 font-medium">~</span>
          <div className="flex-1 relative">
            <input
              type="text"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#999" strokeWidth="1.5">
                <rect x="3" y="4" width="14" height="14" rx="2" />
                <path d="M3 8h14M7 2v4M13 2v4" />
              </svg>
            </div>
          </div>
        </div>

        {/* Search Button */}
        <button
          onClick={handleSearch}
          className="w-full py-4 bg-black text-white font-semibold rounded-xl hover:bg-gray-900 transition-colors"
        >
          Search
        </button>
      </div>

      {/* Results Area - Empty State */}
      <div className="flex-1"></div>

      {/* Chat Button */}
      <div className="fixed bottom-24 right-6">
        <button className="flex items-center gap-2 bg-white shadow-lg rounded-full pl-4 pr-5 py-3 hover:shadow-xl transition-shadow">
          <span className="text-sm text-gray-700">Chat with us</span>
          <div className="w-12 h-12 bg-gradient-to-br from-pink-400 to-blue-500 rounded-full flex items-center justify-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
              <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
            </svg>
          </div>
        </button>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 max-w-[430px] mx-auto">
        <div className="flex items-center justify-around py-3">
          <button className="flex flex-col items-center p-2">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
          <button className="flex flex-col items-center p-2">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
          </button>
          <button className="flex flex-col items-center p-2">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-pink-400 via-purple-400 to-blue-500 flex items-center justify-center">
              <span className="text-white text-xs font-bold">Style<br/>Korean</span>
            </div>
          </button>
          <button className="flex flex-col items-center p-2">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
            </svg>
          </button>
          <button className="flex flex-col items-center p-2">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </button>
        </div>
      </nav>
    </div>
  );
}
