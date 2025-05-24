import axios from 'axios';

// Configure global axios defaults 
// Use relative URLs to work with Vite's proxy
axios.defaults.baseURL = '';
axios.defaults.withCredentials = true;
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

// Mock data for development without backend
const mockData = {
  homeData: {
    stats: {
      total_songs: 432,
      distinct_eras: 8,
      sheet_tabs: [
        { id: 1, name: "V1", icon: "🔴", count: 78 },
        { id: 2, name: "V2", icon: "🟠", count: 120 },
        { id: 3, name: "WLR", icon: "🟣", count: 64 },
        { id: 4, name: "Post-WLR", icon: "⚫", count: 89 },
        { id: 5, name: "Narcissist", icon: "⚪", count: 53 },
        { id: 6, name: "MUSIC", icon: "🔵", count: 28 }
      ]
    },
    recent_songs: Array(10).fill(null).map((_, i) => ({
      id: i + 1,
      name: `Example Song ${i + 1}`,
      producer: `Producer ${i % 3 ? 'Metro Boomin' : i % 2 ? 'Pierre Bourne' : 'Wheezy'}`,
      features: i % 2 ? 'Lil Uzi Vert' : '',
      era: ['V1', 'V2', 'WLR', 'Post-WLR', 'MUSIC'][i % 5],
      quality: ['CDQ', 'HQ', 'LQ'][i % 3],
      preview_file_exists: true,
      preview_audio_url: '/sample-audio.mp3'
    }))
  },
  songs: {
    songs: Array(25).fill(null).map((_, i) => ({
      id: i + 1,
      name: `Example Song ${i + 1}`,
      producer: `Producer ${i % 3 ? 'Metro Boomin' : i % 2 ? 'Pierre Bourne' : 'Wheezy'}`,
      features: i % 2 ? 'Lil Uzi Vert' : '',
      era: ['V1', 'V2', 'WLR', 'Post-WLR', 'MUSIC'][i % 5],
      quality: ['CDQ', 'HQ', 'LQ'][i % 3],
      type: ['Studio', 'Snippet', 'Open Verse'][i % 3],
      primary_tab_name: ['V1', 'V2', 'WLR', 'Post-WLR', 'MUSIC'][i % 5],
      preview_file_exists: true,
      preview_audio_url: '/sample-audio.mp3'
    })),
    filters: {
      pagination: {
        current_page: 1,
        total_pages: 10,
        items_per_page: 25,
        total_items: 250
      },
      current_filters: {},
      eras: ['V1', 'V2', 'WLR', 'Post-WLR', 'Narcissist', 'MUSIC'],
      qualities: ['CDQ', 'HQ', 'LQ'],
      types: ['Studio', 'Snippet', 'Open Verse', 'Instrumental'],
      sheet_tabs: [
        { id: 1, name: "V1", count: 78 },
        { id: 2, name: "V2", count: 120 },
        { id: 3, name: "WLR", count: 64 },
        { id: 4, name: "Post-WLR", count: 89 },
        { id: 5, name: "Narcissist", count: 53 },
        { id: 6, name: "MUSIC", count: 28 }
      ]
    }
  },
  songDetails: {
    id: 1,
    name: "Example Song",
    producer: "Metro Boomin",
    features: "Lil Uzi Vert",
    era: "V2",
    quality: "CDQ",
    type: "Studio",
    primary_tab_name: "V2",
    secondary_tab_names: ["Favorites", "Grails"],
    preview_file_exists: true,
    preview_audio_url: '/sample-audio.mp3',
    leak_date: "2023-05-15",
    file_date: "2023-04-20",
    track_length: "3:42",
    available_length: "Full",
    notes: "This is an example song for the UI prototype."
  }
};

// Simulate network delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Base API service for handling API requests
const apiService = {
  // Download a song and prepare for streaming services
  prepareForStreamingService: async (songId, service) => {
    try {
      // In a real implementation, this would call a backend endpoint
      // that handles the download and prepares it for the specified service
      console.log(`Preparing song ${songId} for ${service}`);
      
      // Mock implementation
      await delay(500);
      return {
        success: true,
        message: `Song prepared for ${service}`,
        instructions: `Here are your instructions for importing to ${service}...`
      };
    } catch (error) {
      console.error(`Error preparing song for ${service}:`, error);
      throw error;
    }
  },

  // Get all songs with optional filters
  getSongs: async (filters = {}) => {
    try {
      console.log('Fetching songs with filters:', filters);
      
      // Try to use real API first
      try {
        const queryParams = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
          if (value) queryParams.append(key, value);
        });
        
        const response = await axios.get(`/api/songs/?${queryParams.toString()}`);
        return response.data;
      } catch (error) {
        console.warn('Using mock data for songs (API server may not be running)');
        await delay(300); // Simulate network delay
        
        // Apply any filters to mock data
        const mockResponse = { ...mockData.songs };
        if (filters.sheet_tab) {
          const tabId = parseInt(filters.sheet_tab);
          const tabName = mockResponse.filters.sheet_tabs.find(tab => tab.id === tabId)?.name;
          mockResponse.songs = mockResponse.songs.filter(song => song.primary_tab_name === tabName);
          mockResponse.filters.current_filters = { ...filters };
        }
        
        return mockResponse;
      }
    } catch (error) {
      console.error('Error fetching songs:', error);
      throw error;
    }
  },
  
  // Get single song details
  getSongDetails: async (songId) => {
    try {
      // Try real API first
      try {
        const response = await axios.get(`/api/songs/${songId}/`);
        return response.data;
      } catch (error) {
        console.warn(`Using mock data for song ${songId} (API server may not be running)`);
        await delay(300); // Simulate network delay
        
        // Return mock song details
        return { 
          ...mockData.songDetails,
          id: parseInt(songId),
          name: `Example Song ${songId}`
        };
      }
    } catch (error) {
      console.error(`Error fetching song ${songId}:`, error);
      throw error;
    }
  },
  
  // Get home page data
  getHomeData: async () => {
    try {
      // Try real API first
      try {
        const response = await axios.get('/api/home/');
        return response.data;
      } catch (error) {
        console.warn('Using mock data for home (API server may not be running)');
        await delay(300); // Simulate network delay
        return mockData.homeData;
      }
    } catch (error) {
      console.error('Error fetching home data:', error);
      throw error;
    }
  },
  
  // Vote on a song
  voteSong: async (songId, vote) => {
    try {
      // Try real API first
      try {
        const response = await axios.post(`/api/songs/${songId}/vote/`, { vote });
        return response.data;
      } catch (error) {
        console.warn(`Using mock data for voting on song ${songId} (API server may not be running)`);
        await delay(300); // Simulate network delay
        return { success: true, message: "Vote recorded (mock)" };
      }
    } catch (error) {
      console.error(`Error voting on song ${songId}:`, error);
      throw error;
    }
  },
  
  // Helper for error handling
  handleApiError: (error) => {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data.error || 'Server error',
        status: error.response.status,
        details: error.response.data.details || null
      };
    } else if (error.request) {
      // Request made but no response
      return {
        message: 'No response from server. Please check your connection.',
        status: 0,
        details: null
      };
    } else {
      // Request setup error
      return {
        message: error.message || 'An unexpected error occurred',
        status: 0,
        details: null
      };
    }
  }
};

export default apiService;