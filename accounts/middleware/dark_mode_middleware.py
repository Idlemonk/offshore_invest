class DarkModeMiddleware:
    """Add dark mode preference to every request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user has dark mode preference
        if request.user.is_authenticated:
            try:
                request.dark_mode = request.user.metadata.dark_mode
            except:
                request.dark_mode = True
        else:
            request.dark_mode = request.session.get('dark_mode', True)
        
        response = self.get_response(request)
        return response
