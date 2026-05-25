export interface BeautyProfile {
  gender?: string;
  ageGroup?: string;
  skinTone?: string;
  skinConcerns: string[];
  healthConcerns: string[];
  cleanBeautyPreferences: string[];
  skinType?: string;
  hairConcerns: string[];
}

export interface SelectableOption {
  id: string;
  label: string;
}
