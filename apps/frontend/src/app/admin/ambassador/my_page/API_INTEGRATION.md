# Ambassador My Page - API Integration

## Overview
This page is integrated with the Spring Boot backend using TanStack Query for data fetching with automatic fallback to mock data.

## Architecture

### Files Structure
- `api.ts` - API client functions for backend communication
- `providers.tsx` - TanStack Query provider setup
- `page.tsx` - Main page component with data fetching
- `mock-data.ts` - Fallback mock data (preserved)
- `types.ts` - TypeScript interfaces

### API Endpoints
All endpoints are prefixed with `/api/v1/`:

1. **OP-001** - `checkAmbassadorStatus()`
   - Returns: `{ profile, socialChannels, rewards }`
   - Used for: Initial page data load

2. **OP-002** - `submitReview()`
   - Used for: Submitting user reviews

3. **OP-003** - `generateSnsLink(platform)`
   - Returns: `{ link }`
   - Used for: Generating social media sharing links

## Configuration

### Environment Variables
Set `NEXT_PUBLIC_API_URL` to override the default backend URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8080/api
```

If not set, defaults to `http://localhost:8080/api`.

## Data Flow

1. **With Backend Running**:
   - Page loads → API call to `/api/v1/OP-001`
   - Success → Display backend data
   - Error → Fall back to mock data

2. **Without Backend Running**:
   - API call fails → Automatically use mock data
   - Page renders normally with mock data

## Loading States
- Shows "Loading..." screen during initial data fetch
- Uses TanStack Query's built-in caching (1 minute stale time)
- Retries once on failure before falling back to mock data

## Testing

### With Backend
```bash
# Start backend on port 8080
# Then start frontend
npm run dev
# Visit: http://localhost:3000/admin/ambassador/my_page
```

### Without Backend
```bash
# Just start frontend (backend off)
npm run dev
# Page will automatically use mock data
```

## Implementation Notes

- Uses `useQuery` hook for data fetching
- Implements automatic retry (1 attempt)
- Preserves all original styling and layout
- No visual changes to the UI
- Mock data serves as both fallback and data contract reference
