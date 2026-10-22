from datetime import date

def needs_renewal(expires_on, as_of=None, within_days=60):
    """True only for a known expiry today through the next within_days days."""
    as_of = as_of or date.today()
    if not expires_on:
        return False
    try:
        days = (date.fromisoformat(expires_on) - as_of).days
    except (ValueError, TypeError):
        return False
    return 0 <= days <= within_days
