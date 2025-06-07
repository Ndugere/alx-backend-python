from datetime import datetime, time
from django.http import HttpResponseForbidden

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
