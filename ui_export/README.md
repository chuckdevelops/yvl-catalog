# Carti Catalog UI Export

This export contains the UI components of the Playboi Carti music catalog project.

## Directory Structure

- `templates/`: HTML templates
  - `base.html`: Base template with navbar and common layout
  - `index.html`: Homepage template
  - `song_detail.html`: Song detail page template
- `css/`: CSS stylesheets
  - `style.css`: Main stylesheet
- `js/`: JavaScript files
  - `album-interaction.js`: Album interaction functionality
  - `audio-manager.js`: Audio player management
  - `audio-url-fixer.js`: Audio URL fixing utilities

## Current UI Design

The current UI is based on Bootstrap 5 with custom styling for music catalog elements. Key features include:

1. A minimalist navbar with search functionality
2. Card-based layout for displaying song information
3. Audio player with various source options
4. Table-based layout for song listings
5. Badge system for song categorization

## UI Theme

The UI currently uses a light theme with the following characteristics:
- White backgrounds with subtle gray accents
- Dark text for readability
- Blue primary accent color with additional badge colors
- Bootstrap-based responsive design

## Notes for UI Reviewers

When reviewing the UI, please consider:
1. Overall aesthetic consistency
2. Mobile responsiveness
3. Audio player user experience
4. Table and card readability
5. Color scheme effectiveness
6. Potential dark mode implementation
7. Badge and categorization visual hierarchy

## Integration Instructions

After review and modifications, please provide:
1. Modified template files
2. Any new CSS files
3. Notes on design changes
4. Mock-ups or screenshots of proposed changes

The team will implement these changes in the Django application.