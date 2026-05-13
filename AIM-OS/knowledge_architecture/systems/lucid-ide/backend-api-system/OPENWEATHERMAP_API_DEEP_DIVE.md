---
id: "openweathermap_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "OpenWeatherMap API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of OpenWeatherMap API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["openweathermap", "weather", "api-integration", "deep-dive"]
---

# OpenWeatherMap API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of OpenWeatherMap API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://openweathermap.org/api

---

## 🎯 **OPENWEATHERMAP API OVERVIEW**

OpenWeatherMap provides comprehensive weather data:
- **Current Weather** - Current conditions
- **Forecast** - 5-day/3-hour forecast, 16-day forecast
- **Historical Data** - Historical weather data
- **Weather Maps** - Weather map layers
- **Air Pollution** - Air quality data
- **UV Index** - UV index data
- **Geocoding** - Location to coordinates

**Key Features:**
- Real-time weather data
- Multiple forecast types
- Historical data
- Weather maps
- Free tier available

---

## 🔐 **AUTHENTICATION**

**Method:** API Key (Query Parameter)

**Query Parameter:**
```
appid=YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://openweathermap.org/api
- Store securely in environment variable: `OPENWEATHERMAP_API_KEY`
- Free tier: 60 calls/minute, 1,000,000 calls/month

**Base URL:**
```
https://api.openweathermap.org/data/2.5
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Current Weather**

**Endpoint:** `GET https://api.openweathermap.org/data/2.5/weather`

**Purpose:** Get current weather conditions

**Query Parameters:**

```typescript
interface OpenWeatherMapCurrentRequest {
  // Required (one of)
  q?: string                        // City name (e.g., 'London')
  lat?: number                      // Latitude
  lon?: number                      // Longitude
  id?: number                       // City ID
  
  // Optional
  units?: 'standard' | 'metric' | 'imperial'  // Temperature units (default: 'kelvin')
  lang?: string                     // Language code (e.g., 'en', 'es')
  mode?: 'json' | 'xml' | 'html'   // Response format (default: 'json')
  
  // Required
  appid: string                     // API key
}
```

**Response Structure:**

```typescript
interface OpenWeatherMapCurrentResponse {
  coord: {
    lon: number
    lat: number
  }
  weather: Array<{
    id: number
    main: string                    // e.g., 'Clear', 'Clouds', 'Rain'
    description: string             // e.g., 'clear sky', 'few clouds'
    icon: string                    // Icon code
  }>
  base: string
  main: {
    temp: number                    // Temperature
    feels_like: number              // Feels like temperature
    temp_min: number                // Min temperature
    temp_max: number                // Max temperature
    pressure: number                // Atmospheric pressure (hPa)
    humidity: number                // Humidity (%)
    sea_level?: number              // Sea level pressure
    grnd_level?: number             // Ground level pressure
  }
  visibility: number                // Visibility (meters)
  wind: {
    speed: number                   // Wind speed (m/s)
    deg: number                     // Wind direction (degrees)
    gust?: number                   // Wind gust
  }
  clouds: {
    all: number                     // Cloudiness (%)
  }
  rain?: {
    '1h'?: number                   // Rain volume for last hour (mm)
    '3h'?: number                   // Rain volume for last 3 hours (mm)
  }
  snow?: {
    '1h'?: number                   // Snow volume for last hour (mm)
    '3h'?: number                   // Snow volume for last 3 hours (mm)
  }
  dt: number                        // Time of data calculation (Unix timestamp)
  sys: {
    type: number
    id: number
    country: string                 // Country code
    sunrise: number                 // Sunrise time (Unix timestamp)
    sunset: number                  // Sunset time (Unix timestamp)
  }
  timezone: number                  // Shift in seconds from UTC
  id: number                        // City ID
  name: string                      // City name
  cod: number                       // Internal parameter
}
```

---

### **2. 5 Day / 3 Hour Forecast**

**Endpoint:** `GET https://api.openweathermap.org/data/2.5/forecast`

**Purpose:** Get 5-day weather forecast with 3-hour intervals

**Query Parameters:**

```typescript
interface OpenWeatherMapForecastRequest {
  // Same as Current Weather
  q?: string
  lat?: number
  lon?: number
  id?: number
  units?: 'standard' | 'metric' | 'imperial'
  lang?: string
  mode?: 'json' | 'xml' | 'html'
  appid: string
}
```

**Response:**

```typescript
interface OpenWeatherMapForecastResponse {
  cod: string
  message: number
  cnt: number                       // Number of forecast items
  list: Array<{
    dt: number                      // Forecast time (Unix timestamp)
    main: {
      temp: number
      feels_like: number
      temp_min: number
      temp_max: number
      pressure: number
      sea_level: number
      grnd_level: number
      humidity: number
      temp_kf: number               // Temperature difference
    }
    weather: Array<{
      id: number
      main: string
      description: string
      icon: string
    }>
    clouds: {
      all: number
    }
    wind: {
      speed: number
      deg: number
      gust: number
    }
    visibility: number
    pop: number                     // Probability of precipitation (0-1)
    rain?: {
      '3h': number
    }
    snow?: {
      '3h': number
    }
    sys: {
      pod: 'd' | 'n'                // Part of day (day/night)
    }
    dt_txt: string                  // Forecast time (ISO 8601)
  }>
  city: {
    id: number
    name: string
    coord: {
      lat: number
      lon: number
    }
    country: string
    population: number
    timezone: number
    sunrise: number
    sunset: number
  }
}
```

---

### **3. One Call API 3.0**

**Endpoint:** `GET https://api.openweathermap.org/data/3.0/onecall`

**Purpose:** Comprehensive weather data (current, minutely, hourly, daily, alerts)

**Query Parameters:**

```typescript
interface OpenWeatherMapOneCallRequest {
  lat: number                       // Required
  lon: number                       // Required
  exclude?: string                  // Comma-separated: 'current', 'minutely', 'hourly', 'daily', 'alerts'
  units?: 'standard' | 'metric' | 'imperial'
  lang?: string
  appid: string                     // Required
}
```

**Response:**

```typescript
interface OpenWeatherMapOneCallResponse {
  lat: number
  lon: number
  timezone: string
  timezone_offset: number
  current: {
    dt: number
    sunrise: number
    sunset: number
    temp: number
    feels_like: number
    pressure: number
    humidity: number
    dew_point: number
    uvi: number                     // UV index
    clouds: number
    visibility: number
    wind_speed: number
    wind_deg: number
    wind_gust?: number
    weather: Array<{...}>
    rain?: {
      '1h': number
    }
    snow?: {
      '1h': number
    }
  }
  minutely?: Array<{
    dt: number
    precipitation: number
  }>
  hourly?: Array<{
    dt: number
    temp: number
    feels_like: number
    pressure: number
    humidity: number
    dew_point: number
    uvi: number
    clouds: number
    visibility: number
    wind_speed: number
    wind_deg: number
    wind_gust?: number
    weather: Array<{...}>
    pop: number                     // Probability of precipitation
    rain?: {
      '1h': number
    }
    snow?: {
      '1h': number
    }
  }>
  daily?: Array<{
    dt: number
    sunrise: number
    sunset: number
    moonrise: number
    moonset: number
    moon_phase: number
    summary: string
    temp: {
      day: number
      min: number
      max: number
      night: number
      eve: number
      morn: number
    }
    feels_like: {
      day: number
      night: number
      eve: number
      morn: number
    }
    pressure: number
    humidity: number
    dew_point: number
    wind_speed: number
    wind_deg: number
    wind_gust?: number
    weather: Array<{...}>
    clouds: number
    pop: number
    rain?: number
    snow?: number
    uvi: number
  }>
  alerts?: Array<{
    sender_name: string
    event: string
    start: number
    end: number
    description: string
    tags: string[]
  }>
}
```

---

### **4. Air Pollution**

**Endpoint:** `GET https://api.openweathermap.org/data/2.5/air_pollution`

**Purpose:** Get air pollution data

**Query Parameters:**

```typescript
interface OpenWeatherMapAirPollutionRequest {
  lat: number                       // Required
  lon: number                       // Required
  appid: string                     // Required
}
```

**Response:**

```typescript
interface OpenWeatherMapAirPollutionResponse {
  coord: {
    lon: number
    lat: number
  }
  list: Array<{
    dt: number
    main: {
      aqi: number                  // Air Quality Index (1-5)
    }
    components: {
      co: number                   // CO concentration
      no: number                   // NO concentration
      no2: number                  // NO2 concentration
      o3: number                   // O3 concentration
      so2: number                  // SO2 concentration
      pm2_5: number                // PM2.5 concentration
      pm10: number                 // PM10 concentration
      nh3: number                  // NH3 concentration
    }
  }>
}
```

---

### **5. Geocoding**

**Endpoint:** `GET https://api.openweathermap.org/geo/1.0/direct` (Forward) or `/reverse` (Reverse)

**Purpose:** Convert location names to coordinates and vice versa

**Query Parameters:**

```typescript
interface OpenWeatherMapGeocodingRequest {
  q?: string                        // Location name (for forward)
  lat?: number                      // Latitude (for reverse)
  lon?: number                      // Longitude (for reverse)
  limit?: number                    // Number of results (default: 5)
  appid: string
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Current Weather**

1. User enters city name or coordinates
2. Get current weather → Display:
   - Temperature
   - Weather condition
   - Humidity, pressure, wind
   - Sunrise/sunset
   - Weather icon

### **Workflow 2: Forecast**

1. User enters location
2. Get 5-day forecast → Display:
   - Daily forecast cards
   - Hourly forecast (expandable)
   - Temperature chart
   - Precipitation probability

### **Workflow 3: One Call (Comprehensive)**

1. User enters coordinates
2. Get one call data → Display:
   - Current conditions
   - Hourly forecast (48 hours)
   - Daily forecast (7 days)
   - Minutely precipitation (next hour)
   - Weather alerts

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 60 calls/minute
- 1,000,000 calls/month

**Paid Tier:**
- Higher rate limits
- More features

---

## 💰 **PRICING**

**Free Tier:**
- 60 calls/minute
- Free forever

**Paid Tier:**
- $40/month for Startup
- Higher rate limits
- Historical data access

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Current Weather Panel**

**Location Input:**
- City name input with autocomplete
- Or coordinate inputs

**Current Conditions:**
- Large temperature display
- Weather icon
- Condition description
- Feels like temperature
- Humidity, pressure, wind display
- Sunrise/sunset times

### **Forecast Panel**

**Daily Forecast:**
- Daily forecast cards
- Date, icon, high/low temps
- Precipitation probability
- Click → Expand hourly forecast

**Hourly Forecast:**
- Hourly timeline
- Temperature chart
- Precipitation chart
- Wind chart

**Charts:**
- Temperature line chart
- Precipitation bar chart
- Wind speed chart

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class OpenWeatherMapService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('openweathermap', 'https://api.openweathermap.org/data/2.5', apiKey)
  }

  async getCurrentWeather(request: OpenWeatherMapCurrentRequest): Promise<APIResponse<OpenWeatherMapCurrentResponse>>
  async getForecast(request: OpenWeatherMapForecastRequest): Promise<APIResponse<OpenWeatherMapForecastResponse>>
  async getOneCall(request: OpenWeatherMapOneCallRequest): Promise<APIResponse<OpenWeatherMapOneCallResponse>>
  async getAirPollution(lat: number, lon: number): Promise<APIResponse<OpenWeatherMapAirPollutionResponse>>
  async geocode(request: OpenWeatherMapGeocodingRequest): Promise<APIResponse<any>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium

**Estimated Implementation Time:**
- Service layer: 3-4 hours
- UI components: 5-6 hours
- Chart integration: 3-4 hours
- Testing: 2-3 hours
- **Total: 13-17 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

