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

MAX_TEXT_LENGTH = 100

def valid_iso_date(value):
    """True only for a real date written exactly as YYYY-MM-DD."""
    if not isinstance(value, str):
        return False
    try:
        # comparing back to the input rejects other ISO forms Python accepts, e.g. 20261018
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False

def validate_trainee(data, today=None, courses=None):
    """Return (clean_values, errors). The data is acceptable only when errors is empty.
    When a list of courses is given, the course must be exactly one of them."""
    today = today or date.today()
    clean, errors = {}, {}
    for field in ('name', 'course'):
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = 'is required'
        elif not isinstance(value, str):
            errors[field] = 'must be text'
        elif len(value.strip()) > MAX_TEXT_LENGTH:
            errors[field] = f'must be at most {MAX_TEXT_LENGTH} characters'
        else:
            clean[field] = value.strip()
    if courses is not None and 'course' in clean and clean['course'] not in courses:
        errors['course'] = 'must be an existing course'
    expires_on = data.get('expires_on')
    if expires_on is None:
        clean['expires_on'] = None
    elif not valid_iso_date(expires_on):
        errors['expires_on'] = 'must be null or a real date in YYYY-MM-DD format'
    elif date.fromisoformat(expires_on) < today:
        errors['expires_on'] = 'must be today or later'
    else:
        clean['expires_on'] = expires_on
    return clean, errors

# the same words as the status badges in web/index.html
STATUS_SOON = 'Renewal soon'
STATUS_NOT_SOON = 'No upcoming renewal'

def matches_search(row, term):
    """True when term appears, in any letter case, in the participant, course,
    expiry date or status that the table shows for this trainee."""
    shown = [
        row['name'],
        row['course'],
        row['expires_on'] or 'Unknown',
        STATUS_SOON if row['renewal_soon'] else STATUS_NOT_SOON,
    ]
    term = term.strip().lower()
    return any(term in text.lower() for text in shown)
