'use client';

import { useState } from 'react';
import { mockAccountSettings, months, days, years } from './mock-data';
import { AccountSettings } from './types';

export default function AccountSettingsPage() {
  const [settings, setSettings] = useState<AccountSettings>(mockAccountSettings);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  return (
    <div className="min-h-screen bg-white pb-32" style={{ width: '430px', margin: '0 auto' }}>
      {/* Header */}
      <div className="flex items-center justify-center relative px-4 py-4 border-b border-gray-200">
        <button className="absolute left-4">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M15 18L9 12L15 6" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <h1 className="text-lg font-medium">Account Settings</h1>
      </div>

      {/* Form Content */}
      <div className="px-4 pt-6">
        {/* First Name */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">First Name</label>
          <input
            type="text"
            placeholder="First Name"
            value={settings.firstName}
            onChange={(e) => setSettings({ ...settings, firstName: e.target.value })}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Last Name */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Last Name</label>
          <input
            type="text"
            placeholder="Last Name"
            value={settings.lastName}
            onChange={(e) => setSettings({ ...settings, lastName: e.target.value })}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Email ID */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Email ID</label>
          <div className="w-full px-4 py-3 bg-gray-100 rounded-lg text-gray-600">
            {settings.emailId}
          </div>
        </div>

        {/* Date of Birth */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Date of Birth</label>
          <div className="flex gap-3">
            <select
              value={settings.dateOfBirth.month}
              onChange={(e) => setSettings({
                ...settings,
                dateOfBirth: { ...settings.dateOfBirth, month: parseInt(e.target.value) }
              })}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              style={{ backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 1rem center', backgroundSize: '1.2em' }}
            >
              {months.map((month) => (
                <option key={month.value} value={month.value}>
                  {month.label}
                </option>
              ))}
            </select>
            <select
              value={settings.dateOfBirth.day}
              onChange={(e) => setSettings({
                ...settings,
                dateOfBirth: { ...settings.dateOfBirth, day: parseInt(e.target.value) }
              })}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              style={{ backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 1rem center', backgroundSize: '1.2em' }}
            >
              {days.map((day) => (
                <option key={day.value} value={day.value}>
                  {day.label}
                </option>
              ))}
            </select>
            <select
              value={settings.dateOfBirth.year}
              onChange={(e) => setSettings({
                ...settings,
                dateOfBirth: { ...settings.dateOfBirth, year: parseInt(e.target.value) }
              })}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              style={{ backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 1rem center', backgroundSize: '1.2em' }}
            >
              {years.map((year) => (
                <option key={year.value} value={year.value}>
                  {year.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Divider */}
        <div className="h-2 bg-gray-100 -mx-4 mb-6"></div>

        {/* Current Password */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Current Password</label>
          <input
            type="password"
            placeholder="Current Password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* New Password */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">New Password</label>
          <input
            type="password"
            placeholder="New Password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Confirm Password */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Confirm Password</label>
          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Divider */}
        <div className="h-2 bg-gray-100 -mx-4 mb-6"></div>

        {/* Help Section */}
        <div className="text-center mb-6">
          <p className="text-sm mb-1">Need help?</p>
          <p className="text-sm">
            Please leave your inquiry on our Q&A chatbot{' '}
            <button className="underline font-medium">(Click here)</button>
          </p>
        </div>

        {/* Delete Account Button */}
        <button className="w-full py-3 bg-gray-400 text-white rounded-lg font-medium mb-6">
          Delete Account
        </button>
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200" style={{ maxWidth: '430px', margin: '0 auto' }}>
        <div className="flex items-center justify-around px-4 py-3">
          <button className="flex flex-col items-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
          <button className="flex flex-col items-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </button>
          <div className="relative -mt-6">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-pink-400 via-purple-400 to-blue-400 flex items-center justify-center shadow-lg">
              <div className="text-white text-[9px] font-bold leading-tight text-center">
                Style<br/>Korean
              </div>
            </div>
          </div>
          <button className="flex flex-col items-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
            </svg>
          </button>
          <button className="flex flex-col items-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </button>
        </div>
      </div>

      {/* Chat Button */}
      <button className="fixed bottom-20 right-4 z-50">
        <div className="relative">
          <div className="absolute -top-1 -left-2 bg-white px-2 py-0.5 rounded-full shadow-md whitespace-nowrap text-xs text-gray-700 font-medium">
            Chat with us
          </div>
          <div className="w-14 h-14 rounded-full bg-pink-400 flex items-center justify-center shadow-lg">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
        </div>
      </button>
    </div>
  );
}
