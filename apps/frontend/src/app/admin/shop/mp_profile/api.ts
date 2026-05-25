import { BeautyProfile } from './types';

const API_BASE_URL = 'http://localhost:8080/api';
const API_TIMEOUT = 3000;

interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: string | null;
}

interface BeautyProfileDto {
  gender: string;
  ageGroup: string;
  skinTone: string;
  skinConcern: string[];
  healthConcern: string[];
  cleanBeautyPreferences: string[];
  skinType: string;
  hairConcern: string[];
}

export async function getBeautyProfile(userId: string = 'user123'): Promise<BeautyProfile | null> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/v1/shop/profile?userId=${userId}`,
      { signal: AbortSignal.timeout(API_TIMEOUT) }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result: ApiResponse<BeautyProfileDto> = await response.json();

    if (!result.success || !result.data) {
      return null;
    }

    // Map backend DTO to frontend type
    return {
      gender: result.data.gender,
      ageGroup: result.data.ageGroup,
      skinTone: result.data.skinTone,
      skinConcerns: result.data.skinConcern || [],
      healthConcerns: result.data.healthConcern || [],
      cleanBeautyPreferences: result.data.cleanBeautyPreferences || [],
      skinType: result.data.skinType,
      hairConcerns: result.data.hairConcern || [],
    };
  } catch (error) {
    console.error('Failed to fetch beauty profile:', error);
    return null;
  }
}

export async function saveBeautyProfile(
  profile: BeautyProfile,
  userId: string = 'user123'
): Promise<boolean> {
  try {
    // Map frontend type to backend DTO
    const dto = {
      gender: profile.gender || '',
      ageGroup: profile.ageGroup || '',
      skinTone: profile.skinTone || '',
      skinConcern: profile.skinConcerns || [],
      healthConcern: profile.healthConcerns || [],
      cleanBeautyPreferences: profile.cleanBeautyPreferences || [],
      skinType: profile.skinType || '',
      hairConcern: profile.hairConcerns || [],
    };

    const response = await fetch(
      `${API_BASE_URL}/v1/shop/profile?userId=${userId}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dto),
        signal: AbortSignal.timeout(API_TIMEOUT),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result: ApiResponse<BeautyProfileDto> = await response.json();
    return result.success;
  } catch (error) {
    console.error('Failed to save beauty profile:', error);
    return false;
  }
}
