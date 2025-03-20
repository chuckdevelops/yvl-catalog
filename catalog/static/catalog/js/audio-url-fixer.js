/**
 * Audio URL Fixer
 * This script ensures audio URLs use the standardized format for all previews
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('[AudioURLFixer] Script loaded and running');
    
    // Wait a moment to ensure all audio elements are fully loaded
    setTimeout(() => {
        // Fix audio URLs immediately
        const fixedCount = fixAudioUrls();
        
        // Log info message with count of fixed URLs
        console.info(`[AudioURLFixer] Fixed ${fixedCount} audio URLs on page load`);
        
        // Log all audio elements on the page for debugging
        const audioElements = document.querySelectorAll('audio');
        console.log(`[AudioURLFixer] Found ${audioElements.length} audio elements on page:`);
        audioElements.forEach((audio, index) => {
            const source = audio.querySelector('source');
            const sourceUrl = source ? source.getAttribute('src') : 'No source element';
            console.log(`[AudioURLFixer] Audio #${index+1}: ${sourceUrl}`);
            
            // Monitor the audio elements for errors
            audio.addEventListener('error', (e) => {
                console.warn(`[AudioURLFixer] Audio error on element #${index+1}:`, e);
                console.log(`[AudioURLFixer] Audio error code:`, audio.error ? audio.error.code : 'No error code');
                
                // Add more detailed error information
                if (audio.error) {
                    switch(audio.error.code) {
                        case MediaError.MEDIA_ERR_ABORTED:
                            console.log('[AudioURLFixer] Error: Media playback aborted by user');
                            break;
                        case MediaError.MEDIA_ERR_NETWORK:
                            console.log('[AudioURLFixer] Error: Network error while loading media');
                            break;
                        case MediaError.MEDIA_ERR_DECODE:
                            console.log('[AudioURLFixer] Error: Media decoding error - file may be corrupted or unsupported');
                            break;
                        case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
                            console.log('[AudioURLFixer] Error: Media format not supported or file not found');
                            break;
                        default:
                            console.log(`[AudioURLFixer] Unknown error code: ${audio.error.code}`);
                    }
                }
                
                // Try to fix the URL and reload
                fixSingleAudioSource(source);
            });
        });
    }, 500);
    
    // Add event listener for audio error events
    document.addEventListener('error', function(e) {
        if (e.target.tagName === 'AUDIO' || (e.target.tagName === 'SOURCE' && e.target.parentElement.tagName === 'AUDIO')) {
            // On error, try to fix again
            console.warn('[AudioURLFixer] Audio error detected, attempting fix');
            
            // Check if we're dealing with a source or audio element
            const source = e.target.tagName === 'SOURCE' ? e.target : e.target.querySelector('source');
            if (source) {
                fixSingleAudioSource(source);
            }
        }
    }, true); // Use capturing phase to catch the event early
});

/**
 * Fix a single audio source element
 */
function fixSingleAudioSource(source) {
    if (!source) return false;
    
    const originalUrl = source.getAttribute('src');
    if (!originalUrl) return false;
    
    let newUrl = originalUrl;
    
    // Check if this is an audio-serve URL which might be problematic
    if (originalUrl.includes('/audio-serve/')) {
        // Extract UUID or ID from the URL
        const filenamePart = originalUrl.split('/audio-serve/')[1]?.split('?')[0];
        
        if (filenamePart) {
            // Check if it's a UUID format (which is more reliable)
            const uuidMatch = filenamePart.match(/^([0-9a-f-]{8}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{12})\.mp3$/i);
            
            if (uuidMatch) {
                // Use direct media URL with UUID (more reliable)
                const uuid = uuidMatch[1];
                newUrl = `/media/previews/${uuid}.mp3?t=${Math.floor(Date.now()/1000)}`;
                console.log(`[AudioURLFixer] Switching to direct media URL for ${uuid}`);
            } else {
                // For non-UUID formats, still try direct media path
                newUrl = `/media/previews/${filenamePart}?t=${Math.floor(Date.now()/1000)}`;
                console.log(`[AudioURLFixer] Switching non-UUID file to direct media URL: ${filenamePart}`);
            }
        }
    }
    
    // Update source if URL has changed
    if (originalUrl !== newUrl) {
        source.setAttribute('src', newUrl);
        console.log(`[AudioURLFixer] Fixed URL: ${newUrl}`);
        
        // Force reload the audio element
        const audioElement = source.parentElement;
        if (audioElement && audioElement.tagName === 'AUDIO') {
            audioElement.load();
            
            // Try to play after a short delay
            setTimeout(() => {
                audioElement.play()
                    .then(() => console.log('[AudioURLFixer] Successfully started playback after URL fix'))
                    .catch(err => console.error('[AudioURLFixer] Error playing after URL fix:', err));
            }, 300);
        }
        
        return true;
    }
    
    return false;
}

/**
 * Fix audio URLs to standardized format for all audio elements on the page
 */
function fixAudioUrls() {
    const audioSources = document.querySelectorAll('audio source');
    let fixedCount = 0;
    
    console.log(`[AudioURLFixer] Found ${audioSources.length} audio sources to check`);
    
    audioSources.forEach((source, index) => {
        console.log(`[AudioURLFixer] Checking source #${index+1}`);
        if (fixSingleAudioSource(source)) {
            fixedCount++;
        }
    });
    
    // If we found and fixed audio URLs, report success
    if (fixedCount > 0) {
        console.log(`[AudioURLFixer] Successfully fixed ${fixedCount} audio URLs`);
    } else {
        console.log('[AudioURLFixer] No audio URLs needed fixing, but checking alternate approach...');
        
        // Try to find cases where audio elements don't have source elements but direct src
        const audioElements = document.querySelectorAll('audio');
        audioElements.forEach((audio, index) => {
            const src = audio.getAttribute('src');
            if (src && src.includes('/audio-serve/')) {
                // Create a new source element
                const source = document.createElement('source');
                
                // Extract the filename
                const filenamePart = src.split('/audio-serve/')[1]?.split('?')[0];
                if (filenamePart) {
                    // Check if it's a UUID
                    const uuidMatch = filenamePart.match(/^([0-9a-f-]{8}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{12})\.mp3$/i);
                    let newUrl;
                    
                    if (uuidMatch) {
                        const uuid = uuidMatch[1];
                        newUrl = `/media/previews/${uuid}.mp3?t=${Math.floor(Date.now()/1000)}`;
                        console.log(`[AudioURLFixer] Converting UUID to direct media URL: ${uuid}`);
                    } else {
                        // For non-UUID formats, still try direct media path
                        newUrl = `/media/previews/${filenamePart}?t=${Math.floor(Date.now()/1000)}`;
                        console.log(`[AudioURLFixer] Converting non-UUID file to direct media URL: ${filenamePart}`);
                    }
                    
                    // Remove the src from the audio element
                    audio.removeAttribute('src');
                    
                    // Set the source element's src and append it
                    source.setAttribute('src', newUrl);
                    source.setAttribute('type', 'audio/mpeg');
                    audio.appendChild(source);
                    
                    // Reload the audio
                    audio.load();
                    console.log(`[AudioURLFixer] Created new source element with URL: ${newUrl}`);
                    fixedCount++;
                }
                }
            }
        });
    }
    
    return fixedCount;
}