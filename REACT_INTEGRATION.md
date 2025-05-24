# React Integration with Django UI

This document explains how the React components are integrated with the existing Django UI.

## Architecture Overview

We're using a hybrid approach that adds React components to the existing Django templates. This allows us to:

1. Keep the current Django UI intact (server-side rendering)
2. Gradually enhance the UI with React components
3. Avoid a complete rewrite of the frontend

## Setup

The integration uses:
- Webpack for bundling React components
- Babel for JSX transpilation
- npm for dependency management

### Development Workflow

1. Install dependencies:
   ```
   npm install
   ```

2. Start the Webpack development server:
   ```
   npm run dev
   ```

3. Build for production:
   ```
   npm run build
   ```

## Component Usage

### 1. Audio Player Component

The enhanced audio player replaces the standard HTML5 audio element with a more feature-rich player.

#### Usage in Django Templates:

```html
<div 
    data-react-audio-player 
    data-audio-url="{{ song.preview_audio_url }}" 
    data-song-name="{{ song.name }}" 
    data-source-type="preview"
    data-alternative-url="{{ song.direct_audio_url }}"
></div>
```

#### Features:
- Improved playback controls
- Visual progress bar
- Volume controls
- Error handling with fallbacks
- Source type badge display

### 2. Badge Component

Consistent badge styling system used throughout the UI.

#### Usage in Django Templates:

```html
<div 
    data-react-badge 
    data-badge-type="primary" 
    data-badge-text="Released"
    data-badge-removable="false"
></div>
```

#### Available Badge Types:
- primary (blue)
- secondary (gray)
- success (green)
- danger (red)
- warning (yellow)
- info (light blue)
- ai (purple)

#### Outline Variants:
Add "outline-" before any type (e.g., "outline-primary")

## Adding New Components

To add a new React component:

1. Create your component in `/catalog/static/catalog/js/react/components/`
2. Import and register it in `index.js`
3. Add an entry point in `webpack.config.js` if needed
4. Create container elements in Django templates with appropriate data attributes

## Future Enhancements

Planned React component additions:
- Card view toggle for the song list
- AJAX filtering system
- Enhanced collection management
- Mobile-optimized media player

## Troubleshooting

If components aren't rendering:
1. Check browser console for errors
2. Verify the correct data attributes are set
3. Run `npm run build` to ensure latest components are bundled
4. Clear browser cache (`localStorage.cache_version` is updated on changes)