# React Integration Guide for Carti Catalog

This guide explains how the React integration works with the Django backend to create a Single Page Application (SPA) experience.

## Architecture Overview

- **Frontend**: React SPA built with Vite, TypeScript, and shadcn/ui components
- **Backend**: Django serving both API endpoints and the SPA entry point
- **Communication**: REST API endpoints (/api/songs/, etc.) consumed by React hooks

## Building the React App

1. To build the React application, run:
   ```bash
   ./build_react.sh
   ```

   This script:
   - Installs npm dependencies
   - Builds the React app with Vite
   - Copies the built bundle to Django's static directories

2. The built files are placed at:
   - JS: `catalog/static/catalog/js/dist/bundle.js`
   - CSS: `catalog/static/catalog/css/bundle.css`

## Django Integration

### URL Routing

- Django handles routing for API endpoints and the SPA
- All non-API routes point to the `react_app` view (SPA catch-all)
- Client-side routing using React Router handles in-app navigation

### API Endpoints

Main API endpoints used by the React app:

- `GET /api/songs/`: List all songs with filtering and pagination
- `GET /api/songs/{id}/`: Get details for a specific song
- `POST /api/songs/{id}/vote/`: Vote on a song (like/dislike)

### Template

The SPA entry point is `catalog/templates/catalog/react_app.html`, which:
- Loads React bundles
- Provides initial loading UI
- Makes Django context available to React via `window` variables

## Front-end Components

### Structure

- `src/App.tsx`: Main component with React Router setup
- `src/hooks/useSongFiltering.ts`: Hook for API data fetching
- `src/data/songs.ts`: API client functions and types
- `src/pages/`: Individual page components (SongList, SongDetail, etc.)
- `src/components/`: Reusable UI components

### Data Flow

1. React components use custom hooks to fetch data from API endpoints
2. Data is transformed and stored in local state
3. Components render based on this state (loading/error/data)
4. User interactions trigger API calls to update data

### API Client

The API client in `src/data/songs.ts` includes:
- TypeScript interfaces for strong typing
- Fetch functions with error handling
- CSRF token management for protected endpoints

## Troubleshooting

### Common Issues

1. **"Loading Carti Catalog" stuck**:
   - Check browser console for errors
   - Ensure bundle.js is being loaded correctly
   - Verify static files are found

2. **API errors**:
   - Check Network tab in dev tools
   - Verify API endpoints are working as expected
   - Check CSRF token is available

3. **Build errors**:
   - Install missing npm dependencies
   - Update components with breaking changes
   - Verify package versions are compatible

## Development Workflow

1. Run the Django development server (`./manage.py runserver`)
2. For React development:
   - Option 1: Run Vite dev server (`cd hello-ui-feedback && npm run dev`)
   - Option 2: Use the build script with watch mode

3. After making React changes, rebuild using `./build_react.sh`
4. Refresh the Django page to see changes