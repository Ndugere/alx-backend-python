import os
from datetime import datetime
from django.conf import settings
from django.http import HttpResponseForbidden


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        
        log_file_path = os.path.join(settings.BASE_DIR, 'requests.log')
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_entry)
        
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for chat-related URLs
        if request.path.startswith('/chats/'):
            current_hour = datetime.now().hour
            
            # Restrict access outside 9 AM (9) to 6 PM (18)
            # The task says "outside 9PM and 6PM" but logically it should be 9AM to 6PM
            # If you need 9PM to 6PM (overnight), use: if not (current_hour >= 21 or current_hour < 6):
            if not (9 <= current_hour <= 18):
                return HttpResponseForbidden("Access to chat is restricted outside business hours (9 AM - 6 PM).")
        
        response = self.get_response(request)
        return response