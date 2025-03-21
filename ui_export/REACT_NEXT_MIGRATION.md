# Migrating to React and Next.js

This document outlines a strategy for migrating the current Django-based Carti Catalog UI to a modern React + Next.js frontend while maintaining Django as the backend API.

## Benefits of React + Next.js

1. **Improved User Experience**
   - Client-side navigation (faster page transitions)
   - React's component-based architecture for reusable UI elements
   - More interactive elements without full page reloads

2. **Performance Enhancements**
   - Code splitting and lazy loading
   - Static site generation for faster initial page loads
   - Image optimization

3. **Developer Experience**
   - Modern JavaScript/TypeScript ecosystem
   - Hot module replacement during development
   - Strong typing with TypeScript

## Architecture Strategy

### Backend (Django)
- Convert Django views to API endpoints returning JSON
- Implement REST API using Django REST Framework
- Keep all database models and business logic in Django
- Implement proper CORS handling for the separate frontend

### Frontend (Next.js)
- Create new Next.js application
- Build React components based on existing Django templates
- Use Next.js API routes to proxy requests to Django backend when needed
- Implement authentication with JWT or similar token-based system

## Component Structure

The React components would mirror the structure of the current templates:

```
components/
  layout/
    Header.jsx          # Converted from navbar in base.html
    Footer.jsx          # Converted from footer in base.html
    Layout.jsx          # Main layout wrapper
  
  songs/
    SongList.jsx        # Converted from song_list.html
    SongFilters.jsx     # Filter section from song_list.html
    SongTable.jsx       # Results table from song_list.html
    Pagination.jsx      # Pagination controls
    
    SongDetail.jsx      # Converted from song_detail.html
    SongMetadata.jsx    # Song metadata table
    AudioPlayer.jsx     # Enhanced audio player
    ExternalLinks.jsx   # External source links
    RecommendedSongs.jsx # Sidebar recommendations
    
  common/
    Badge.jsx           # Reusable badge component
    Card.jsx            # Reusable card component
    Table.jsx           # Base table component
    Button.jsx          # Styled button component
```

## UI Improvements with React

1. **Enhanced Audio Player**
   - Custom React-based audio player with waveform visualization
   - Persistent player across page navigation
   - Playlist functionality

2. **Dynamic Filtering**
   - Real-time filtering without page reloads
   - Interactive filter chips/tags
   - Save filter preferences

3. **Theme System**
   - Smooth theme transitions
   - Multiple theme options
   - Per-user theme preferences

4. **Animations and Transitions**
   - Page transition animations
   - Micro-interactions for improved feedback
   - Loading states and skeletons

## Implementation Steps

1. **Setup Next.js Project**
   ```bash
   npx create-next-app@latest carti-catalog-frontend --typescript
   ```

2. **Create Core Components**
   - Convert the HTML templates to React components
   - Implement styling with CSS modules, styled-components, or Tailwind CSS

3. **Set Up API Integration**
   - Create services to fetch data from Django backend
   - Implement data fetching with SWR or React Query

4. **Authentication Flow**
   - Implement login/signup if required
   - Set up protected routes

5. **Progressive Enhancement**
   - Start with core functionality
   - Add enhancements incrementally
   - Focus on maintaining all current features before adding new ones

## Example Component (SongCard)

```jsx
// components/songs/SongCard.jsx
import React from 'react';
import Link from 'next/link';
import { Badge } from '../common/Badge';
import styles from './SongCard.module.css';

export const SongCard = ({ song }) => {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <Link href={`/songs/${song.id}`}>
          <h3 className={styles.title}>{song.name}</h3>
        </Link>
        {song.preview_url && (
          <span className={styles.audioIndicator}>
            <i className="fas fa-music" />
          </span>
        )}
      </div>
      
      <div className={styles.metadata}>
        <div className={styles.era}>{song.era || 'Unknown Era'}</div>
        <div className={styles.categories}>
          {song.primary_tab_name && (
            <Badge variant="primary">{song.primary_tab_name}</Badge>
          )}
          {song.emoji_tab_names?.map(tab => (
            <Badge key={tab} variant="info">{tab}</Badge>
          ))}
        </div>
      </div>
      
      {song.preview_url && (
        <div className={styles.audioPreview}>
          <AudioPlayer url={song.preview_url} />
        </div>
      )}
    </div>
  );
};
```

## Deployment Considerations

1. **Hosting Options**
   - Vercel (optimal for Next.js)
   - Netlify
   - AWS Amplify

2. **Backend Integration**
   - Ensure Django backend is accessible to the Next.js application
   - Consider using Next.js API routes as a proxy when needed

3. **Environment Setup**
   - Environment variables for API endpoints
   - Separate development/production configurations

## Potential Challenges

1. **Authentication**
   - Transitioning from session-based to token-based auth
   - Maintaining secure communication between frontend and backend

2. **SEO Considerations**
   - Ensuring proper SEO with server-side rendering or static generation

3. **Initial Development Overhead**
   - React + Next.js learning curve if team is primarily Django-focused
   - Time investment in recreating existing functionality

## Next Steps

1. Create a proof-of-concept with core pages (home, song list, song detail)
2. Review with stakeholders for feedback
3. Develop a phased migration plan
4. Consider running both UIs in parallel during transition

---

This document provides a high-level overview of the migration strategy. Each step would require detailed planning and implementation.