from datetime import datetime
import logging
import os
from django.conf import settings

# Configure logging to write to requests.log file
log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')

# Create a custom logger for request logging
logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)

# Create file handler if it doesn't exist
if not logger.handlers:
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    
    # Create formatter - only log the message without extra formatting
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)

class RequestLoggingMiddleware:
    """
    Basic middleware that logs each user's requests to a file.
    Logs timestamp, user, and request path in the specified format.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response callable.
        
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Process the request and log the information.
        
        Args:
            request: The HTTP request object
            
        Returns:
            HTTP response from the next middleware/view
        """
        # Get the user (handle both authenticated and anonymous users)
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username
        else:
            user = 'Anonymous'
        
        # Log the request information in the exact specified format
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Call the next middleware or view
        response = self.get_response(request)
        
        return response