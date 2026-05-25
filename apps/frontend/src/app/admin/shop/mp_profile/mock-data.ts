import { BeautyProfile, SelectableOption } from './types';

export const mockProfile: BeautyProfile = {
  gender: 'Female',
  ageGroup: '30s',
  skinTone: 'Fair',
  skinConcerns: ['Dark Spots', 'Anti-Aging'],
  healthConcerns: ['Sleep Stress'],
  cleanBeautyPreferences: ['Cruelty Free'],
  skinType: 'Combination',
  hairConcerns: ['Damaged Hair'],
};

export const genderOptions: SelectableOption[] = [
  { id: 'male', label: 'Male' },
  { id: 'female', label: 'Female' },
  { id: 'others', label: 'Others' },
];

export const ageGroupOptions: SelectableOption[] = [
  { id: '-16', label: '~16' },
  { id: '17-19', label: '17-19' },
  { id: '20s', label: '20s' },
  { id: '30s', label: '30s' },
  { id: '40s', label: '40s' },
  { id: '50s+', label: '50s~' },
];

export const skinToneOptions: SelectableOption[] = [
  { id: 'porcelain', label: 'Porcelain' },
  { id: 'fair', label: 'Fair' },
  { id: 'medium', label: 'Medium' },
  { id: 'tan', label: 'Tan' },
  { id: 'olive', label: 'Olive' },
  { id: 'deep', label: 'Deep' },
  { id: 'dark', label: 'Dark' },
  { id: 'ebony', label: 'Ebony' },
];

export const skinConcernOptions: SelectableOption[] = [
  { id: 'acne', label: 'Acne' },
  { id: 'dark-spots', label: 'Dark Spots' },
  { id: 'dryness', label: 'Dryness' },
  { id: 'anti-aging', label: 'Anti-Aging' },
  { id: 'wrinkle-care', label: 'Wrinkle Care' },
  { id: 'oil-control', label: 'Oil Control' },
  { id: 'soothing', label: 'Soothing' },
  { id: 'calming', label: 'Calming' },
  { id: 'pore-care', label: 'Pore Care' },
];

export const healthConcernOptions: SelectableOption[] = [
  { id: 'chronic-fatigue', label: 'Chronic Fatigue' },
  { id: 'sleep-stress', label: 'Sleep Stress' },
  { id: 'weight-loss', label: 'Weight Loss' },
  { id: 'immunity-boost', label: 'Immunity Boost' },
  { id: 'skin-health', label: 'Skin Health' },
  { id: 'gut-health', label: 'Gut Health' },
];

export const cleanBeautyOptions: SelectableOption[] = [
  { id: 'vegan', label: 'Vegan' },
  { id: 'cruelty-free', label: 'Cruelty Free' },
  { id: 'not-interested', label: 'Not Interested' },
];

export const skinTypeOptions: SelectableOption[] = [
  { id: 'oily', label: 'Oily' },
  { id: 'dry', label: 'Dry' },
  { id: 'normal', label: 'Normal' },
  { id: 'combination', label: 'Combination' },
  { id: 'sensitive', label: 'Sensitive' },
];

export const hairConcernOptions: SelectableOption[] = [
  { id: 'hair-loss', label: 'Hair Loss' },
  { id: 'damaged-hair', label: 'Damaged Hair' },
  { id: 'weakened-scalp', label: 'Weakened Scalp' },
  { id: 'hot-scalp', label: 'Hot Scalp' },
  { id: 'oily-scalp', label: 'Oily Scalp' },
  { id: 'itchy-scalp', label: 'Itchy Scalp' },
];
