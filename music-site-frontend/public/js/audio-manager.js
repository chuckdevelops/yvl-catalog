/**
 * Audio Player Manager
 * Centralizes audio player functionality and handles pagination
 * Now with PHYSICS!
 */
class AudioPlayerManager {
    constructor() {
        this.players = new Map();
        this.activePlayer = null;
        this.maxPlayers = 3; // Maximum number of simultaneously initialized players
        this.initialized = false;
        this.physicsEnabled = false;
        this.physicsObjects = [];
    }

    /**
     * Initialize the audio manager
     */
    init() {
        if (this.initialized) return;
        
        console.log('[AudioManager] Initializing');
        
        // Create a global event for pagination navigation
        window.addEventListener('paginationNavigate', () => {
            this.refreshPlayers();
        });
        
        // Handle page visibility changes to pause audio when tab is hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.activePlayer) {
                this.activePlayer.pause();
            }
        });
        
        // Set up pagination link interceptors
        this.setupPaginationLinks();
        
        // Initial page scan
        this.refreshPlayers();
        
        this.initialized = true;
    }
    
    /**
     * Set up interception of pagination link clicks to trigger player refresh
     */
    setupPaginationLinks() {
        const paginationLinks = document.querySelectorAll('.pagination .page-link');
        paginationLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // Let the browser navigate, but trigger our event after a delay
                setTimeout(() => {
                    window.dispatchEvent(new CustomEvent('paginationNavigate'));
                }, 100);
            });
        });
    }
    
    /**
     * Scan the page for audio players and initialize or refresh them
     */
    refreshPlayers() {
        console.log('[AudioManager] Refreshing players');
        
        // Clear existing players
        this.players.clear();
        
        // Find all audio elements on the page
        const audioElements = document.querySelectorAll('audio[data-player-id]');
        
        // Queue initialization for visible players first
        const visiblePlayers = Array.from(audioElements).filter(el => this.isElementVisible(el));
        const hiddenPlayers = Array.from(audioElements).filter(el => !this.isElementVisible(el));
        
        // Initialize visible players first
        visiblePlayers.forEach(player => this.registerPlayer(player));
        
        // Initialize a limited number of hidden players
        hiddenPlayers.slice(0, this.maxPlayers - visiblePlayers.length).forEach(player => this.registerPlayer(player));
        
        // Re-setup pagination links (in case new ones were added)
        this.setupPaginationLinks();
    }
    
    /**
     * Register and initialize an audio player
     */
    registerPlayer(playerElement) {
        if (!playerElement || !playerElement.dataset.playerId) return;
        
        const playerId = playerElement.dataset.playerId;
        if (this.players.has(playerId)) return;
        
        console.log(`[AudioManager] Registering player: ${playerId}`);
        
        // Add cache-busting to source URL
        const sourceElement = playerElement.querySelector('source');
        if (sourceElement) {
            // Use seconds rather than milliseconds for timestamp
            const timestamp = Math.floor(Date.now() / 1000);
            let url = sourceElement.src;
            
            // If URL has no timestamp, add one
            if (url && !url.includes('t=')) {
                if (url.includes('?')) {
                    sourceElement.src = `${url}&t=${timestamp}`;
                } else {
                    sourceElement.src = `${url}?t=${timestamp}`;
                }
            }
        }
        
        // Find status element
        const statusElement = document.getElementById(`${playerId}-status`);
        
        // Create player object
        const player = {
            element: playerElement,
            sourceElement,
            statusElement,
            isPlaying: false,
            hasError: false,
            isInitialized: false,
            metadata: {}
        };
        
        // Register event handlers
        this.setupPlayerEvents(player);
        
        // Store player in map
        this.players.set(playerId, player);
        
        // Explicitly load the player
        playerElement.load();
        
        return player;
    }
    
    /**
     * Setup event handlers for a player
     */
    setupPlayerEvents(player) {
        const { element, statusElement } = player;
        
        // Metadata loaded
        element.addEventListener('loadedmetadata', () => {
            console.log(`[AudioManager] Metadata loaded for player: ${player.element.dataset.playerId}`);
            player.isInitialized = true;
            player.metadata.duration = element.duration;
            
            if (statusElement) {
                statusElement.style.display = 'none';
            }
            
            // If duration is invalid, try to reload
            if (isNaN(element.duration) || element.duration === 0) {
                console.warn('[AudioManager] Invalid duration, attempting to reload');
                this.reloadPlayer(player);
            }
        });
        
        // Error handling
        element.addEventListener('error', (e) => {
            console.error(`[AudioManager] Error with player: ${player.element.dataset.playerId}`, element.error);
            
            // Get detailed error info if available
            let errorDetails = 'Unknown error';
            if (element.error) {
                switch(element.error.code) {
                    case MediaError.MEDIA_ERR_ABORTED:
                        errorDetails = 'Playback aborted by user';
                        break;
                    case MediaError.MEDIA_ERR_NETWORK:
                        errorDetails = 'Network error while loading audio';
                        break;
                    case MediaError.MEDIA_ERR_DECODE:
                        errorDetails = 'Audio decoding error - file may be corrupted';
                        break;
                    case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
                        errorDetails = 'Audio format not supported or file not found';
                        break;
                    default:
                        errorDetails = `Error code: ${element.error.code}`;
                }
            }
            console.error(`[AudioManager] Error details: ${errorDetails}`);
            console.log(`[AudioManager] Current source URL: ${element.src}`);
            
            player.hasError = true;
            
            if (statusElement) {
                statusElement.textContent = `Error: ${errorDetails}. Trying alternative...`;
                statusElement.style.display = 'block';
            }
            
            // First, check if there's a preview URL in the page we can use
            const previewUrlElement = document.querySelector('.small.text-muted.mb-2 code');
            if (previewUrlElement) {
                const previewUrl = previewUrlElement.innerText;
                if (previewUrl && previewUrl.includes('/media/previews/')) {
                    console.log(`[AudioManager] Found preview URL in page: ${previewUrl}`);
                    // Extract UUID from preview URL
                    const uuidMatch = previewUrl.match(/\/media\/previews\/([0-9a-f-]{8}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{12})\.mp3/i);
                    if (uuidMatch && uuidMatch[1]) {
                        const uuid = uuidMatch[1];
                        const timestamp = new Date().getTime();
                        const newUrl = `/audio-serve/${uuid}.mp3?t=${timestamp}`;
                        
                        console.log(`[AudioManager] Trying with UUID from preview URL: ${uuid}`);
                        sourceElement.src = newUrl;
                        element.load();
                        setTimeout(() => {
                            element.play().catch(err => {
                                console.error('[AudioManager] Error playing with UUID:', err);
                            });
                        }, 500);
                        return;
                    }
                }
            }
            
            // Check if this is an external source
            const sourceElement = player.sourceElement;
            if (sourceElement && sourceElement.dataset.externalSource) {
                // Extract song ID from external source URL
                const externalSource = sourceElement.dataset.externalSource;
                const songIdMatch = externalSource.match(/\/song\/([a-f0-9]+)\/play/);
                
                if (songIdMatch && songIdMatch[1]) {
                    // We have a song ID - use it directly
                    const songId = songIdMatch[1];
                    const timestamp = new Date().getTime();
                    const newUrl = `/audio-serve/${songId}.mp3?t=${timestamp}`;
                    
                    console.log(`[AudioManager] Using song ID for player with error: ${songId}`);
                    sourceElement.src = newUrl;
                    element.load();
                    setTimeout(() => {
                        element.play().catch(err => {
                            console.error('[AudioManager] Error playing with song ID:', err);
                        });
                    }, 500);
                    return;
                }
            }
            
            // Check if current URL contains a hash or external ID
            // and try to switch to a direct media URL approach
            const currentSrc = element.src || (sourceElement && sourceElement.src);
            if (currentSrc && currentSrc.includes('/audio-serve/')) {
                // Try to use direct media URL instead of audio-serve
                const parts = currentSrc.split('/audio-serve/');
                if (parts.length > 1) {
                    const filename = parts[1].split('?')[0];
                    const timestamp = new Date().getTime();
                    const directUrl = `/media/previews/${filename}?t=${timestamp}`;
                    
                    console.log(`[AudioManager] Trying direct media URL: ${directUrl}`);
                    if (sourceElement) {
                        sourceElement.src = directUrl;
                    } else {
                        element.src = directUrl;
                    }
                    element.load();
                    setTimeout(() => {
                        element.play().catch(err => {
                            console.error('[AudioManager] Error playing with direct URL:', err);
                            
                            // Additional retry with minimal settings
                            console.log('[AudioManager] Retrying with minimal settings...');
                            const simpleUrl = `/media/previews/${filename}`;
                            if (sourceElement) {
                                sourceElement.src = simpleUrl;
                            } else {
                                element.src = simpleUrl;
                            }
                            element.load();
                            element.play().catch(finalErr => {
                                console.error('[AudioManager] Final error with minimal URL:', finalErr);
                            });
                        });
                    }, 500);
                    return;
                }
            }
            
            // Try to reload after a short delay
            setTimeout(() => this.reloadPlayer(player), 1000);
        });
        
        // Play event
        element.addEventListener('play', () => {
            console.log(`[AudioManager] Playback started: ${player.element.dataset.playerId}`);
            player.isPlaying = true;
            
            // Pause any other playing audio
            this.pauseOtherPlayers(player.element.dataset.playerId);
            
            // Set as active player
            this.activePlayer = element;
            
            if (statusElement) {
                statusElement.style.display = 'none';
            }
        });
        
        // Pause event
        element.addEventListener('pause', () => {
            player.isPlaying = false;
            if (this.activePlayer === element) {
                this.activePlayer = null;
            }
        });
        
        // Ended event
        element.addEventListener('ended', () => {
            player.isPlaying = false;
            if (this.activePlayer === element) {
                this.activePlayer = null;
            }
        });
    }
    
    /**
     * Play audio with specified URL
     */
    playAudio(playerId, audioUrl, limitDuration = false) {
        // Get or register player
        let player = this.players.get(playerId);
        if (!player) {
            const element = document.getElementById(playerId);
            if (!element) {
                console.error(`[AudioManager] Player not found: ${playerId}`);
                return false;
            }
            player = this.registerPlayer(element);
        }
        
        const { element, statusElement } = player;
        
        // Add cache-busting parameter if not already present
        if (!audioUrl.includes('t=')) {
            // Use seconds rather than milliseconds for consistency
            const timestamp = Math.floor(Date.now() / 1000);
            if (audioUrl.includes('?')) {
                audioUrl = `${audioUrl}&t=${timestamp}`;
            } else {
                audioUrl = `${audioUrl}?t=${timestamp}`;
            }
        }
        
        // Update status
        if (statusElement) {
            statusElement.textContent = 'Loading audio...';
            statusElement.style.display = 'block';
        }
        
        // Remove existing timeupdate listeners
        element.removeEventListener('timeupdate', this.durationLimitHandler);
        
        // Set audio source
        element.src = audioUrl;
        
        // Force reload to ensure new source is used
        element.load();
        
        // Add event listener for timeupdate if limiting duration
        if (limitDuration) {
            element.addEventListener('timeupdate', this.durationLimitHandler);
        }
        
        // Start playing after a short delay to allow metadata loading
        setTimeout(() => {
            element.play()
                .then(() => {
                    console.log('[AudioManager] Playback started successfully');
                    if (statusElement) {
                        statusElement.style.display = 'none';
                    }
                })
                .catch(e => {
                    console.error('[AudioManager] Error playing audio:', e);
                    if (statusElement) {
                        statusElement.textContent = 'Error starting playback. Please try again.';
                        statusElement.style.display = 'block';
                    }
                });
        }, 300);
        
        return true;
    }
    
    /**
     * Reload a player with a new timestamp, using song ID for external sources
     */
    reloadPlayer(player) {
        const { element, sourceElement } = player;
        
        if (sourceElement) {
            // Check if this is an external source with song ID
            const externalSource = sourceElement.dataset.externalSource;
            let srcUrl;
            
            if (externalSource) {
                // Extract song ID from external source URL
                const songIdMatch = externalSource.match(/\/song\/([a-f0-9]+)\/play/);
                
                if (songIdMatch && songIdMatch[1]) {
                    // We have a song ID - use it as the filename
                    const songId = songIdMatch[1];
                    const timestamp = new Date().getTime();
                    srcUrl = `/audio-serve/${songId}.mp3?t=${timestamp}`;
                    console.log(`[AudioManager] Reloading with song ID: ${songId}`);
                } else {
                    // No song ID found - use existing URL format with new timestamp
                    const timestamp = new Date().getTime();
                    // Get the base URL without query parameters
                    const baseUrl = sourceElement.src.split('?')[0];
                    srcUrl = `${baseUrl}?t=${timestamp}`;
                }
            } else {
                // Local source - check if it's a UUID-based URL (which we should prioritize)
                const timestamp = new Date().getTime();
                const currentUrl = sourceElement.src;
                
                // Check if we have a UUID in the current URL
                const uuidMatch = currentUrl.match(/\/audio-serve\/([0-9a-f-]{8}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{12})\.mp3/i);
                
                if (uuidMatch && uuidMatch[1]) {
                    // We have a UUID - use it directly with a new timestamp
                    const uuid = uuidMatch[1];
                    srcUrl = `/audio-serve/${uuid}.mp3?t=${timestamp}`;
                    console.log(`[AudioManager] Reloading with UUID: ${uuid}`);
                } else {
                    // No UUID found - use base URL with a new timestamp
                    const baseUrl = sourceElement.src.split('?')[0];
                    srcUrl = `${baseUrl}?t=${timestamp}`;
                }
            }
            
            // Update source and reload
            sourceElement.src = srcUrl;
            element.load();
            console.log(`[AudioManager] Reloaded player with new src: ${srcUrl}`);
        }
    }
    
    /**
     * Pause all other players except the one specified
     */
    pauseOtherPlayers(currentPlayerId) {
        this.players.forEach((player, id) => {
            if (id !== currentPlayerId && player.isPlaying) {
                player.element.pause();
            }
        });
    }
    
    /**
     * Check if an element is visible in viewport
     */
    isElementVisible(el) {
        if (!el) return false;
        
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    /**
     * Duration limit handler function - removed 20-second limitation
     */
    durationLimitHandler() {
        // No duration limit - allow full playback
        return;
    }
}

// Create global audio manager instance
window.audioPlayerManager = new AudioPlayerManager();

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    window.audioPlayerManager.init();
});

// Duration limit handler (static method to allow removal) - removed 20-second limitation
AudioPlayerManager.prototype.durationLimitHandler = function() {
    // No duration limit - allow full playback
    return;
}; 