import logging
from datetime import datetime
from datetime import datetime, time
from django.http import HttpResponseForbidden
from django.http import JsonResponse

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Configure logger
        self.logger = logging.getLogger('django.request_logging')
        handler = logging.FileHandler('requests.log')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        current_time = datetime.now().time()
        start_time = time(18, 0)
        end_time = time(21, 0) 

        if not (start_time <= current_time <= end_time):
            return HttpResponseForbidden(
                "Access to the chat is only allowed between 6 PM and 9 PM."
            )

        return self.get_response(request)
    

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
     
        self.ip_message_times = {}

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/messages/"):
            ip = self.get_client_ip(request)
            now = time.time()
            window = 60
            limit = 5    

            
            times = self.ip_message_times.get(ip, [])

            
            times = [t for t in times if now - t < window]

            if len(times) >= limit:
                
                return JsonResponse(
                    {"error": "Too many messages sent. Please wait before sending more."},
                    status=429
                )

            
            times.append(now)
            self.ip_message_times[ip] = times

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class RolepermissionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user = request.user
            if not (user.is_superuser or user.groups.filter(name__in=["admin", "moderator"]).exists()):
                return HttpResponseForbidden("403 Forbidden: You do not have the required role to access this resource.")
        
        return self.get_response(request)