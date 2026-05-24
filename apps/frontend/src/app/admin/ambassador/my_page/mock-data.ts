import { SocialChannel, AmbassadorReward, AmbassadorProfile } from './types';

export const ambassadorProfile: AmbassadorProfile = {
  name: 'Aimee',
  country: 'Singapore',
  birthday: 'February 14, 1998',
  sns: 'A1234567B',
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
    icon: '💅',
    title: 'Monthly Product Highlights',
    description: 'Get exclusive access to the latest beauty trends via our official channel.',
  },
  {
    icon: '💜',
    title: 'Free Products to Try',
    description: 'Get access to our newest trending K-beauty products.',
  },
  {
    icon: '🤝',
    title: 'Exciting Brand Collaborations',
    description: 'Get a chance to collaborate with trending K-beauty brands exclusively.',
  },
];
