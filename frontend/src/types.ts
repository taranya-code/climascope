export interface Recommendation {
  title: string;
  rationale: string;
  priority: number;
}

export interface AssessmentReport {
  id: number;
  site_id: number;

  panel_area_m2: number;
  turbine_rotor_area_m2: number;
  turbine_hub_height_m: number;

  solar_daily_kwh: number;
  solar_annual_kwh: number;

  wind_daily_kwh: number;
  wind_annual_kwh: number;
  wind_class: string;
  hub_height_wind_speed_ms: number;

  heat_stress_days_per_year: number;
  cooling_degree_days: number;
  heating_degree_days: number;
  precipitation_variability_index: number;

  monthly_mean_temps_c: number[];
  monthly_max_temps_c: number[];
  monthly_precip_mm_day: number[];

  currency_symbol: string;
  electricity_price_per_kwh: number | null;
  estimated_annual_savings: number | null;
  estimated_monthly_savings: number | null;
  system_cost: number | null;
  payback_years: number | null;

  recommendations: Recommendation[];
  created_at: string;
}

export interface AssessmentRequest {
  lat: number;
  lon: number;
  site_name?: string;
  panel_area_m2: number;
  turbine_rotor_area_m2: number;
  turbine_hub_height_m: number;
  electricity_price_per_kwh?: number;
  currency_symbol?: string;
  system_cost?: number;
}

export interface Site {
  id: number;
  name: string;
  lat: number;
  lon: number;
  created_at: string;
}

export interface PlaceSuggestion {
  name: string;
  country: string | null;
  admin1: string | null;
  lat: number;
  lon: number;
}
