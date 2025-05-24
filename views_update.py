# Add this function to catalog/views.py

def react_updated(request, path=None):
    """
    Serve the updated React Single Page Application
    """
    return render(request, 'catalog/react_updated.html', {
        'timestamp': int(time.time())  # For cache busting
    })