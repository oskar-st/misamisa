from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

class ClearMessagesMiddleware(MiddlewareMixin):
    """
    Middleware to ensure Django messages are properly cleared to prevent
    cross-page contamination, especially with HTMX navigation.
    """
    
    def process_response(self, request, response):
        # For login/register pages, clear any unrelated messages that might have persisted
        if request.path in ['/login/', '/register/', '/resend-verification/']:
            # Get current messages without displaying them
            storage = messages.get_messages(request)
            
            # Check if there are messages that don't belong on auth pages
            auth_related_keywords = ['password', 'email', 'login', 'register', 'verify', 'account']
            
            messages_to_clear = []
            messages_to_keep = []
            
            for message in storage:
                message_text = str(message).lower()
                # If message contains terms unrelated to authentication, mark for clearing
                if not any(keyword in message_text for keyword in auth_related_keywords):
                    if any(term in message_text for term in ['invoice', 'address', 'deleted', 'updated', 'shipping']):
                        messages_to_clear.append(message)
                    else:
                        messages_to_keep.append(message)
                else:
                    messages_to_keep.append(message)
            
            # If we found unrelated messages, clear them
            if messages_to_clear:
                # Clear all messages first
                list(messages.get_messages(request))  # This consumes and clears all messages
                
                # Re-add only the auth-related ones
                for message in messages_to_keep:
                    messages.add_message(request, message.level, message.message, message.tags)
        
        return response 