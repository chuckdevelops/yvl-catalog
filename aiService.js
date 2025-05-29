// AI Service for music-related features
class AIService {
  constructor() {
    this.apiKey = process.env.REACT_APP_OPENAI_API_KEY;
    this.baseUrl = 'https://api.openai.com/v1';
  }

  async analyzeMood(mood) {
    try {
      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: "gpt-4",
          messages: [
            {
              role: "system",
              content: "You are a music mood analyzer. Analyze the given mood and return a JSON object with mood characteristics and music preferences."
            },
            {
              role: "user",
              content: `Analyze this mood and suggest music characteristics: ${mood}`
            }
          ],
          temperature: 0.7
        })
      });

      const data = await response.json();
      return JSON.parse(data.choices[0].message.content);
    } catch (error) {
      console.error('Mood analysis failed:', error);
      throw error;
    }
  }

  async generatePlaylist(prompt, availableSongs) {
    try {
      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: "gpt-4",
          messages: [
            {
              role: "system",
              content: "You are a music playlist generator. Create a playlist based on the user's description and available songs."
            },
            {
              role: "user",
              content: `Create a playlist based on this description: ${prompt}. Available songs: ${JSON.stringify(availableSongs)}`
            }
          ],
          temperature: 0.7
        })
      });

      const data = await response.json();
      return JSON.parse(data.choices[0].message.content);
    } catch (error) {
      console.error('Playlist generation failed:', error);
      throw error;
    }
  }

  async getSongInsights(song) {
    try {
      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: "gpt-4",
          messages: [
            {
              role: "system",
              content: `You are a music analyst specializing in detailed song analysis. 
              Analyze the provided song and return a JSON object with the following structure:
              {
                "analysis": {
                  "mood": "string describing the emotional tone",
                  "genre": "string describing the genre and subgenre",
                  "era": "string describing the musical era",
                  "keyCharacteristics": ["array of key musical characteristics"],
                  "technicalAnalysis": {
                    "tempo": "string describing the tempo",
                    "rhythm": "string describing the rhythm pattern",
                    "instrumentation": ["array of main instruments"],
                    "productionStyle": "string describing the production approach"
                  }
                },
                "similarSongs": [
                  {
                    "name": "string",
                    "artist": "string",
                    "reason": "string explaining why it's similar"
                  }
                ],
                "culturalContext": {
                  "influence": "string describing musical influences",
                  "impact": "string describing the song's impact",
                  "notableElements": ["array of notable musical elements"]
                }
              }`
            },
            {
              role: "user",
              content: `Analyze this song in detail: ${JSON.stringify(song)}`
            }
          ],
          temperature: 0.7
        })
      });

      const data = await response.json();
      const insights = JSON.parse(data.choices[0].message.content);
      
      // Add metadata about the analysis
      insights.metadata = {
        analyzedAt: new Date().toISOString(),
        model: "gpt-4",
        confidence: "high"
      };

      return insights;
    } catch (error) {
      console.error('Song insights failed:', error);
      throw error;
    }
  }

  // Add a new method for batch analysis
  async analyzeSongBatch(songs, analysisType = 'comprehensive') {
    try {
      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: "gpt-4",
          messages: [
            {
              role: "system",
              content: `You are a music analyst specializing in batch analysis of songs. 
              Analyze the provided songs and identify patterns, connections, and relationships between them.
              Return a JSON object with the following structure:
              {
                "commonThemes": ["array of common themes across songs"],
                "moodProgression": ["array describing how moods evolve across songs"],
                "genreConnections": {
                  "primaryGenres": ["array of main genres"],
                  "genreBlends": ["array of genre combinations"],
                  "evolution": "string describing genre evolution across songs"
                },
                "recommendedGroupings": [
                  {
                    "name": "string describing the group",
                    "songs": ["array of song IDs"],
                    "reason": "string explaining the grouping"
                  }
                ],
                "playlistSuggestions": [
                  {
                    "name": "string",
                    "description": "string",
                    "songs": ["array of song IDs"],
                    "flow": "string describing the musical flow"
                  }
                ]
              }`
            },
            {
              role: "user",
              content: `Analyze these songs as a collection: ${JSON.stringify(songs)}`
            }
          ],
          temperature: 0.7
        })
      });

      const data = await response.json();
      return JSON.parse(data.choices[0].message.content);
    } catch (error) {
      console.error('Batch analysis failed:', error);
      throw error;
    }
  }

  // Add a method for real-time analysis during playback
  async getRealTimeInsights(song, currentTime) {
    try {
      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: "gpt-4",
          messages: [
            {
              role: "system",
              content: `You are a music analyst providing real-time insights during song playback.
              Analyze the song at the current timestamp and provide relevant insights.
              Return a JSON object with the following structure:
              {
                "currentSection": {
                  "type": "string (verse, chorus, bridge, etc.)",
                  "characteristics": ["array of musical characteristics"],
                  "significance": "string explaining the section's importance"
                },
                "musicalElements": {
                  "instruments": ["array of active instruments"],
                  "techniques": ["array of notable techniques"],
                  "production": "string describing production elements"
                },
                "emotionalImpact": {
                  "mood": "string describing current mood",
                  "intensity": "number between 0-1",
                  "transitions": "string describing mood changes"
                }
              }`
            },
            {
              role: "user",
              content: `Analyze this song at timestamp ${currentTime}: ${JSON.stringify(song)}`
            }
          ],
          temperature: 0.7
        })
      });

      const data = await response.json();
      return JSON.parse(data.choices[0].message.content);
    } catch (error) {
      console.error('Real-time analysis failed:', error);
      throw error;
    }
  }
}

export default new AIService(); 