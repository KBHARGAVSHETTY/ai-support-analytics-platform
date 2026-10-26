import os
import json
from analytics import get_ticket_statistics

# Fictional support documentation for the AI assistant
SUPPORT_DOCS = {
    "login": "To login to the system, go to the login page and enter your username and password. If you forgot your password, click 'Forgot Password' and follow the instructions sent to your email.",
    "password": "To reset your password, click the 'Forgot Password' link on the login page. You will receive an email with instructions to create a new password.",
    "payment": "For payment issues, first check your payment method details. Ensure your card is not expired and has sufficient funds. If the problem persists, contact billing support.",
    "billing": "Billing inquiries should be directed to our billing department. You can reach them at billing@example.com or call 1-800-BILLING.",
    "dashboard": "The dashboard shows an overview of your support tickets. You can filter tickets by status, priority, or category using the controls at the top of the dashboard.",
    "ticket": "To create a new support ticket, click the 'New Ticket' button, fill in the required fields (title, description, category, priority), and submit. You can update ticket status using the dropdown in the tickets table.",
    "email": "Email notifications are sent for ticket updates. Ensure your email address is correct in your profile settings to receive notifications.",
    "performance": "If the system is running slowly, try clearing your browser cache or using a different browser. For persistent performance issues, contact technical support.",
    "error": "If you encounter an error message, note the exact text and any error codes. Try refreshing the page first. If the error persists, contact support with the error details.",
    "help": "I can help you with common support questions about login, passwords, payments, billing, dashboard usage, ticket creation, email notifications, performance issues, and error messages. I can also provide statistics about your support tickets.",
    "statistics": "I can provide you with current support ticket statistics including total tickets, open tickets, resolved tickets, and breakdowns by category and priority."
}

def get_ai_response(message):
    """
    Generate a response to the user's message.
    Falls back to rule-based responses if no API key is configured.
    """
    # Check if we should use an external LLM API
    api_key = os.environ.get('AI_API_KEY')
    
    if api_key and api_key != 'your_api_key_here':
        # In a real implementation, we would call an external LLM API here
        # For this educational example, we'll stick with the fallback
        # but show how it would be structured
        return get_fallback_response(message)
    else:
        # Use the fallback response system
        return get_fallback_response(message)

def get_fallback_response(message):
    """
    Generate a response using rule-based matching.
    This is the fallback when no API key is available or when we choose not to use it.
    """
    message_lower = message.lower().strip()
    
    # Handle special statistics questions first
    if any(word in message_lower for word in ['statistic', 'statistics', 'how many', 'count', 'total']):
        return get_statistics_response()
    
    # Check for matches in our support documentation
    for key, response in SUPPORT_DOCS.items():
        if key in message_lower:
            return response
    
    # If no match found, return a default response
    return ("I'm sorry, I don't have information about that specific topic. "
            "I can help with common support issues like login problems, password reset, "
            "payment issues, billing questions, dashboard usage, ticket creation, "
            "email notifications, performance issues, and error messages. "
            "I can also provide statistics about your support tickets. "
            "Could you please rephrase your question or ask about one of these topics?")

def get_statistics_response():
    """
    Generate a response containing current ticket statistics.
    """
    try:
        stats = get_ticket_statistics()
        
        if stats['total_tickets'] == 0:
            return ("There are currently no support tickets in the system. "
                    "Once tickets are created, I'll be able to provide you with statistics.")
        
        response_parts = [
            f"Here are the current support ticket statistics:",
            f"- Total tickets: {stats['total_tickets']}",
            f"- Open tickets: {stats['open_tickets']}",
            f"- Resolved tickets: {stats['resolved_tickets']}",
            f"- High priority tickets: {stats['high_priority_tickets']}"
        ]
        
        if stats['tickets_by_category']:
            response_parts.append("- Breakdown by category:")
            for category, count in stats['tickets_by_category'].items():
                response_parts.append(f"  * {category}: {count}")
                
        if stats['tickets_by_priority']:
            response_parts.append("- Breakdown by priority:")
            for priority, count in stats['tickets_by_priority'].items():
                response_parts.append(f"  * {priority}: {count}")
        
        return "\n".join(response_parts)
    except Exception as e:
        # If there's an error getting statistics, fall back to a generic response
        return ("I'm currently unable to retrieve ticket statistics. "
                "Please try again later or contact support if this issue persists.")
