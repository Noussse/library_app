from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def check_password_strength(password):
    try:
        validate_password(password)
        return True, "Password is strong."
    except ValidationError as e:
        return False, e.messages