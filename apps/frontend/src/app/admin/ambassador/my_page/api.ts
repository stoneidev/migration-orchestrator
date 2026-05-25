import { AmbassadorProfile, SocialChannel, AmbassadorReward } from './types';
import { ambassadorProfile as mockProfile, socialChannels as mockSocialChannels, ambassadorRewards as mockRewards } from './mock-data';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';

export interface AmbassadorStatusResponse {
  profile: AmbassadorProfile;
  socialChannels: SocialChannel[];
  rewards: AmbassadorReward[];
}

export async function checkAmbassadorStatus(): Promise<AmbassadorStatusResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/ambassador/my-page/status?memberId=1`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(3000),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  } catch {
    // Fallback to mock data when backend is not available
    return {
      profile: mockProfile,
      socialChannels: mockSocialChannels,
      rewards: mockRewards,
    };
  }
}

export async function submitReview(data: unknown): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/ambassador/my-page/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) throw new Error('Failed');
  } catch {
    console.log('[Mock] Review submitted (backend offline)');
  }
}

export async function generateSnsLink(platform: string): Promise<{ link: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/ambassador/my-page/sns-link`, {
      method: 'POST',
      body: JSON.stringify({ platform }),
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) throw new Error('Failed');
    return response.json();
  } catch {
    return { link: `https://stylekorean.com/ambassador?ref=mock&platform=${platform}` };
  }
}
