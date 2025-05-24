# React UI Integration Guide

This document provides instructions for integrating the new React UI with the existing Django backend.

## Setup Instructions

### Prerequisites

- Node.js v16+ and npm installed
- Django backend running on localhost:8000

### Installation

1. Install the required dependencies:
   ```bash
   npm install react react-dom react-router-dom
   npm install --save-dev @vitejs/plugin-react vite
   npm install --save-dev tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

2. Configure Tailwind CSS:
   Update the `tailwind.config.js` file:
   ```javascript
   module.exports = {
     content: [
       "./*.{js,jsx}",
       "./src/**/*.{js,jsx}",
     ],
     theme: {
       extend: {},
     },
     plugins: [],
   }
   ```

3. Create a `vite.config.js` file:
   ```javascript
   import { defineConfig } from 'vite';
   import react from '@vitejs/plugin-react';

   export default defineConfig({
     plugins: [react()],
     server: {
       port: 3000,
       proxy: {
         '/api': {
           target: 'http://localhost:8000',
           changeOrigin: true,
         },
         '/media': {
           target: 'http://localhost:8000',
           changeOrigin: true,
         }
       }
     },
     build: {
       outDir: 'catalog/static/catalog/js/dist',
       emptyOutDir: true,
       manifest: true,
       rollupOptions: {
         input: {
           main: './index.js',
         },
         output: {
           entryFileNames: 'bundle.js',
           chunkFileNames: '[name].js',
           assetFileNames: '[name].[ext]'
         }
       }
     }
   });
   ```

4. Add the following scripts to your `package.json`:
   ```json
   "scripts": {
     "dev": "vite",
     "build": "vite build",
     "preview": "vite preview"
   }
   ```

## Development Workflow

1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

2. Start the Vite development server for React:
   ```bash
   npm run dev
   ```

3. For production build:
   ```bash
   npm run build
   ```

## Structure

- `App.js`: Main application component with routing
- `Home.js`: Dashboard showing statistics and recent songs
- `List.js`: Song listing with filtering capabilities
- `index.js`: Entry point that mounts the React app
- `index.css`: Global styles

## API Endpoints

The React app interacts with these Django API endpoints:

- `/api/home/`: Provides statistics and recent songs for the homepage
- `/api/songs/`: Lists songs with filtering options
- `/api/songs/<song_id>/`: Gets detailed information about a specific song

## React Router Configuration

The application uses React Router to handle client-side navigation:

- `/`: Home dashboard
- `/list`: Song listing with filters
- `/list?id=<song_id>`: Shows song details

## Integration with Django

This React application is designed to work with the existing Django backend without requiring changes to the backend code. It uses the API endpoints already defined in `catalog/api_views.py`.

To deploy the application, simply build the React app (`npm run build`) and ensure the Django template at `catalog/templates/catalog/react_app.html` is set up to load the generated bundle.