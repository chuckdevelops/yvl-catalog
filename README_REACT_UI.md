# Carti Catalog React UI

This project provides a modern React-based user interface for the Carti Catalog Django application. It enhances the existing functionality with a more interactive and responsive design while maintaining consistency with the original aesthetic.

## Features

- **Dashboard Page**: Overview of catalog statistics and recent additions
- **Song Library**: Searchable and filterable list of songs
- **Song Details**: Detailed view of song information
- **Audio Player**: Embedded audio player for previews
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js 14.x or later
- npm 6.x or later
- Django backend running on localhost:8000

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   ./build_react_new.sh
   ```

## Usage

### Development Mode

During development, you can run the React application with hot reloading:

```bash
npm run dev
```

This starts a dev server at http://localhost:3000 with the following features:
- Hot reloading for instant feedback
- Proxy setup to forward API requests to the Django backend
- Source maps for easier debugging

### Production Build

To create a production build for deployment:

```bash
./build_react_new.sh
```

This will:
1. Install dependencies if needed
2. Build optimized React assets
3. Place the build artifacts in the Django static directory

After building, you can access the React UI through Django at:
```
http://localhost:8000/react-ui/
```

## Project Structure

- `App.js`: Main application component with routing
- `Home.js`: Dashboard component showing statistics and recent songs
- `List.js`: Song list component with filtering and pagination
- `SongDetail.js`: Detailed view of a specific song
- `index.js`: Application entry point
- `index.css`: Global styles and TailwindCSS configuration
- `tailwind.config.js`: TailwindCSS configuration
- `vite.config.js`: Vite bundler configuration

## Integration with Django

This React application integrates with the existing Django backend through:

1. **API Endpoints**: Consumes data from `/api/home/`, `/api/songs/`, etc.
2. **Template Integration**: Embedded in Django templates at `/react-ui/`
3. **Asset Management**: Built files stored in Django's static directory
4. **URL Configuration**: React routing works alongside Django's URL patterns

## Customization

To customize the UI:

1. Colors and theme: Edit `index.css` and `tailwind.config.js`
2. Layout and components: Modify the React components in their respective files
3. API integration: Update the fetch calls in the components if the API changes