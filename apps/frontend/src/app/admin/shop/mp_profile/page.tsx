'use client';

import { useState, useEffect } from 'react';
import { BeautyProfile } from './types';
import SelectionGroup from './components/SelectionGroup';
import {
  mockProfile,
  genderOptions,
  ageGroupOptions,
  skinToneOptions,
  skinConcernOptions,
  healthConcernOptions,
  cleanBeautyOptions,
  skinTypeOptions,
  hairConcernOptions,
} from './mock-data';
import { getBeautyProfile, saveBeautyProfile } from './api';

export default function BeautyProfilePage() {
  const [profile, setProfile] = useState<BeautyProfile>(mockProfile);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const loadProfile = async () => {
      setLoading(true);
      const data = await getBeautyProfile();
      if (data) {
        setProfile(data);
      }
      setLoading(false);
    };
    loadProfile();
  }, []);

  const handleSingleSelect = (field: keyof BeautyProfile, value: string) => {
    setProfile((prev) => ({
      ...prev,
      [field]: prev[field] === value ? undefined : value,
    }));
  };

  const handleMultiSelect = (field: keyof BeautyProfile, value: string) => {
    setProfile((prev) => {
      const currentValues = (prev[field] as string[]) || [];
      const newValues = currentValues.includes(value)
        ? currentValues.filter((v) => v !== value)
        : [...currentValues, value];
      return {
        ...prev,
        [field]: newValues,
      };
    });
  };

  const handleSave = async () => {
    setSaving(true);
    const success = await saveBeautyProfile(profile);
    setSaving(false);
    if (success) {
      alert('Profile saved successfully!');
    } else {
      alert('Failed to save profile. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="sticky top-0 bg-white z-10 flex items-center px-4 py-3 border-b border-gray-200">
        <button className="p-1" aria-label="Go back">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
        <h1 className="flex-1 text-center font-semibold text-lg pr-6">
          Beauty Profile
        </h1>
      </div>

      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-purple-500 via-pink-400 to-blue-400 py-8 px-6 text-center text-white">
        <h2 className="text-2xl font-bold leading-tight">
          What are your
          <br />
          skin type and concerns?
        </h2>
      </div>

      {/* Content */}
      <div className="py-6">
        {loading && (
          <div className="flex justify-center py-12">
            <div className="w-8 h-8 border-4 border-pink-400 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && (
          <>

        {/* Gender */}
        <SelectionGroup
          title="Gender"
          options={genderOptions}
          selected={profile.gender || ''}
          onSelect={(value) => handleSingleSelect('gender', value)}
        />

        {/* Age Group */}
        <SelectionGroup
          title="Age Group"
          options={ageGroupOptions}
          selected={profile.ageGroup || ''}
          onSelect={(value) => handleSingleSelect('ageGroup', value)}
        />

        {/* Skin Tone */}
        <SelectionGroup
          title="Skin Tone"
          options={skinToneOptions}
          selected={profile.skinTone || ''}
          onSelect={(value) => handleSingleSelect('skinTone', value)}
          coloredOptions={true}
        />

        {/* Skin Concern */}
        <SelectionGroup
          title="Skin Concern"
          options={skinConcernOptions}
          selected={profile.skinConcerns}
          onSelect={(value) => handleMultiSelect('skinConcerns', value)}
          multiSelect={true}
        />

        {/* Chat with us button */}
        <div className="fixed bottom-24 right-6 z-20">
          <button
            className="relative bg-gradient-to-r from-pink-400 to-pink-600 text-white rounded-full p-4 shadow-lg"
            aria-label="Chat with us"
          >
            <svg
              className="w-6 h-6"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" />
            </svg>
            <span className="absolute -top-1 -right-2 bg-white text-pink-500 text-[10px] font-semibold px-2 py-0.5 rounded-full whitespace-nowrap shadow-sm">
              Chat with us
            </span>
          </button>
        </div>

        {/* Health Concern */}
        <SelectionGroup
          title="Health Concern"
          options={healthConcernOptions}
          selected={profile.healthConcerns}
          onSelect={(value) => handleMultiSelect('healthConcerns', value)}
          multiSelect={true}
        />

        {/* Clean Beauty Preferences */}
        <SelectionGroup
          title="Clean Beauty Preferences"
          options={cleanBeautyOptions}
          selected={profile.cleanBeautyPreferences}
          onSelect={(value) =>
            handleMultiSelect('cleanBeautyPreferences', value)
          }
          multiSelect={true}
        />

        {/* Skin Type */}
        <SelectionGroup
          title="Skin Type"
          options={skinTypeOptions}
          selected={profile.skinType || ''}
          onSelect={(value) => handleSingleSelect('skinType', value)}
        />

        {/* Hair Concern */}
        <SelectionGroup
          title="Hair Concern"
          options={hairConcernOptions}
          selected={profile.hairConcerns}
          onSelect={(value) => handleMultiSelect('hairConcerns', value)}
          multiSelect={true}
        />

        {/* Privacy Notice */}
        <div className="px-6 py-4 text-xs text-gray-600 leading-relaxed">
          <h3 className="font-semibold text-sm mb-3">
            Collection and Use of Personal Information
          </h3>
          <ul className="list-disc pl-5 space-y-3">
            <li>
              <span className="font-semibold">
                Items of Personal Information Collected:
              </span>{' '}
              Gender, Age, Skin Tone, Skin Type, Skin Concern, Hair Concern,
              Health Concern, Clean Beauty Preferences
            </li>
            <li>
              <span className="font-semibold">
                Purpose of Collection and Use of Personal Information:
              </span>{' '}
              To share your beauty profile with StyleKorean allowing you to view
              product reviews that align with your profile
            </li>
            <li>
              <span className="font-semibold">Retention and Use Period:</span>{' '}
              Your information will be kept until deletion of membership
              cancellation
            </li>
            <li>
              You have the right to refuse to agree in the Preference of Refusal,
              and the option to disagree with the collection and use of your
              personal information. However, if you choose not to consent, you
              will not be able to access the service.
            </li>
          </ul>
        </div>

        {/* Save Button */}
        <div className="px-4 pb-24">
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full bg-black text-white py-4 rounded-lg font-semibold text-base hover:bg-gray-800 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
          </>
        )}
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 flex justify-around items-center">
        <button className="p-2" aria-label="Menu">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <button className="p-2" aria-label="Search">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
        <button className="relative -mt-4" aria-label="StyleKorean">
          <div className="w-14 h-14 bg-gradient-to-br from-pink-400 to-pink-600 rounded-full flex items-center justify-center shadow-lg">
            <div className="text-white text-[8px] font-bold leading-tight text-center">
              STYLE<br />KOREAN
            </div>
          </div>
        </button>
        <button className="p-2" aria-label="Favorites">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </button>
        <button className="p-2" aria-label="Profile">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </button>
      </div>
    </div>
  );
}
