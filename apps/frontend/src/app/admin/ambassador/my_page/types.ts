export interface SocialChannel {
  name: string;
  platform: 'instagram' | 'youtube' | 'tiktok';
  icon: string;
}

export interface AmbassadorReward {
  icon: string;
  title: string;
  description: string;
}

export interface AmbassadorProfile {
  name: string;
  country: string;
  birthDate: string;
  skinType: string;
}
