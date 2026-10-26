import pandas as pd
from database import get_tickets

def get_ticket_statistics():
    """Return ticket statistics as a dictionary using Pandas."""
    # Get all tickets as a list of dictionaries
    tickets_list = get_tickets()
    if not tickets_list:
        # Return zeros if no tickets
        return {
            'total_tickets': 0,
            'open_tickets': 0,
            'resolved_tickets': 0,
            'high_priority_tickets': 0,
            'tickets_by_category': {},
            'tickets_by_priority': {}
        }
    
    # Convert to Pandas DataFrame
    df = pd.DataFrame(tickets_list)
    
    # Calculate statistics
    total_tickets = len(df)
    open_tickets = len(df[df['status'] == 'Open'])
    # Consider resolved as status in ['Resolved', 'Closed']
    resolved_tickets = len(df[df['status'].isin(['Resolved', 'Closed'])])
    high_priority_tickets = len(df[df['priority'] == 'High'])
    
    # Count by category
    tickets_by_category = df['category'].value_counts().to_dict()
    # Count by priority
    tickets_by_priority = df['priority'].value_counts().to_dict()
    
    return {
        'total_tickets': int(total_tickets),
        'open_tickets': int(open_tickets),
        'resolved_tickets': int(resolved_tickets),
        'high_priority_tickets': int(high_priority_tickets),
        'tickets_by_category': tickets_by_category,
        'tickets_by_priority': tickets_by_priority
    }