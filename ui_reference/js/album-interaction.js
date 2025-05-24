// Album interaction functionality

document.addEventListener('DOMContentLoaded', function() {
    // Get all album images
    const albumCovers = document.querySelectorAll('.album-img');
    
    // Add event listeners to each album cover
    albumCovers.forEach(album => {
        // Start spinning on hover for all albums
        album.addEventListener('mouseenter', function() {
            if (!this.classList.contains('spin')) {
                this.classList.add('spin-temp');
            }
        });
        
        // Stop spinning when mouse leaves
        album.addEventListener('mouseleave', function() {
            if (this.classList.contains('spin-temp')) {
                this.classList.remove('spin-temp');
            }
        });
        
        // Toggle permanent spinning on click
        album.addEventListener('click', function(e) {
            // Don't prevent navigation for actual clicks on the album
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                this.classList.toggle('spin');
                if (this.classList.contains('spin-temp')) {
                    this.classList.remove('spin-temp');
                }
            }
        });
    });
    
    // Add spinning CSS dynamically
    const style = document.createElement('style');
    style.textContent = `
        .album-img.spin-temp {
            animation: spin 15s linear infinite;
        }
    `;
    document.head.appendChild(style);
});