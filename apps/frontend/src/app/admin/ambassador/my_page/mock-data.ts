import { SocialChannel, AmbassadorReward, AmbassadorProfile } from './types';

export const ambassadorProfile: AmbassadorProfile = {
  name: 'Adeyel',
  country: 'Barcelona',
  birthDate: '1-January-19',
  skinType: 'Dry',
};

export const socialChannels: SocialChannel[] = [
  {
    name: 'Instagram',
    platform: 'instagram',
    icon: '📷',
  },
  {
    name: 'Youtube',
    platform: 'youtube',
    icon: '▶️',
  },
  {
    name: 'TikTok',
    platform: 'tiktok',
    icon: '🎵',
  },
];

export const ambassadorRewards: AmbassadorReward[] = [
  {
    icon: '💟',
    title: 'Exclusive Product Highlights',
    description: 'Get a chance to be featured across our official channel.',
  },
  {
    icon: '💜',
    title: 'First Access to Free Products',
    description: 'Be the first to experience our trending K-beauty products.',
  },
  {
    icon: '🤝',
    title: 'Build Brand Collaborations',
    description: 'Get a chance to connect with leading K-beauty brands for exciting partnership.',
  },
];
