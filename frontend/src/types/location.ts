// Location and geographical types

export interface PrefectureOption {
  code: string;
  nameJa: string;
  nameEn: string;
}

// Additional location-related types can be added here
export interface LocationData {
  prefecture?: string;
  city?: string;
  address?: string;
  postalCode?: string;
}

export interface CoordinateData {
  latitude: number;
  longitude: number;
}
