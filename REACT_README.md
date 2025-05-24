# React Integration Documentation

This document provides an overview of the React integration in the Carti Catalog project.

## Overview

We've implemented a hybrid approach that integrates React components into the existing Django application while maintaining backward compatibility. This allows us to gradually modernize the UI while preserving existing functionality.

## Key Components

### 1. React Song List

A complete React-based implementation of the song list page is available at `/songs/react/`, living alongside the original Django template-based implementation at `/songs/`. This allows us to:

- Compare both implementations side-by-side
- Gradually migrate users to the React version
- Maintain backward compatibility

### 2. React Audio Player

The enhanced React-based audio player is integrated into the song detail page, providing:

- Improved playback controls
- Visual progress indicator
- Volume controls
- Error handling with fallbacks
- Duration limiting for older browsers
- Consistent styling with visual feedback

## Integration Method

We use the following approach for integrating React components:

1. **Component-Based Integration**: React components are mounted to specific DOM elements using data attributes
2. **Server-Side Data Preparation**: Django views prepare and serialize data for React components
3. **Progressive Enhancement**: React enhances the existing UI rather than replacing it entirely
4. **Parallel URLs**: For larger page components, we maintain both React and Django template versions

## Technical Architecture

- **Webpack**: Bundles React components into a single JavaScript file
- **Babel**: Transpiles JSX and modern JavaScript features
- **Django Templates**: Include the React bundle and define mounting points
- **React 18.2+**: Uses the latest React features and patterns

## Navigation

Users can access both versions of the song list:

1. Using the navigation dropdown menu at the top
2. Using the "Switch to React View" / "Standard View" buttons on each page
3. Directly via URLs:
   - `/songs/` - Standard Django template version
   - `/songs/react/` - React-enhanced version

## Development Workflow

1. Make changes to React components in `/catalog/static/catalog/js/react/`
2. Run the build script to generate the bundle:
   ```
   ./build_react.sh
   ```
   - Or during development:
   ```
   npm run dev
   ```
3. Refresh the browser to see changes

## Future Enhancements

Planned React component additions:
- Card view for the song list
- AJAX-based filter system
- Enhanced mobile experience
- More sophisticated search functionality

## Troubleshooting

If components aren't rendering:
- Check browser console for errors
- Verify the correct data attributes are set
- Run `npm run build` to ensure latest components are bundled
- Clear browser cache (`localStorage.cache_version` is updated automatically)