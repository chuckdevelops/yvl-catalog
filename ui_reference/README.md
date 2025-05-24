# UI Reference Files for Lovable.dev

This folder contains essential files from the original UI that can be used as a reference when building a completely new UI framework from scratch.

## Directory Structure

- `/templates/` - HTML templates including:
  - `base.html` - Basic layout structure
  - `song_list.html` - Song listing page
  - `song_detail.html` - Individual song details page

- `/css/` - CSS styling files:
  - `style.css` - Main CSS styles
  - `design-system.css` - Design system components

- `/js/` - JavaScript functionality:
  - `audio-manager.js` - Audio playback functionality
  - `audio-url-fixer.js` - Audio URL corrections
  - `album-interaction.js` - Album interaction functions

- `/api/` - API integration reference

## How to Use

These files provide a reference for the structure, styling, and functionality of the existing application. When creating a new UI from scratch, you can refer to these files to understand:

1. The expected HTML structure
2. CSS styling patterns
3. JavaScript functionality requirements, especially for audio playback
4. API endpoints and data structures

## Migration Strategy

For a complete UI rewrite, consider using a modern framework like React, Vue, or Svelte with a CSS framework such as Tailwind CSS. The `hello-ui-feedback` folder in the main project already contains a modern implementation using React and Tailwind CSS that you can use as a starting point.

## Important Audio Features

The audio playback features are particularly important to maintain in any new implementation:

- Audio player controls
- Error handling with fallbacks
- Dynamic URL management
- Play/pause functionality across multiple players