import os
from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpResponseForbidden
from collections import defaultdict


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
            if not (9 <= current_hour <= 18):
                return HttpResponseForbidden("Access to chat is restricted outside business hours (9 AM - 6 PM).")
        
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to store IP addresses and their message timestamps
        self.ip_message_tracker = defaultdict(list)
        self.message_limit = 5  # 5 messages per minute
        self.time_window = 60   # 60 seconds (1 minute)

    def __call__(self, request):
        # Only check POST requests to chat endpoints (when sending messages)
        if request.method == 'POST' and request.path.startswith('/chats/'):
            client_ip = self.get_client_ip(request)
            current_time = datetime.now()
            
            # Clean old timestamps (older than 1 minute)
            self.clean_old_timestamps(client_ip, current_time)
            
            # Check if user has exceeded the limit
            if len(self.ip_message_tracker[client_ip]) >= self.message_limit:
                return HttpResponseForbidden("Rate limit exceeded. You can only send 5 messages per minute.")
            
            # Add current timestamp to the tracker
            self.ip_message_tracker[client_ip].append(current_time)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def clean_old_timestamps(self, ip, current_time):
        """Remove timestamps older than the time window"""
        cutoff_time = current_time - timedelta(seconds=self.time_window)
        self.ip_message_tracker[ip] = [
            timestamp for timestamp in self.ip_message_tracker[ip] 
            if timestamp > cutoff_time
        ]