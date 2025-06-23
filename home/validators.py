from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

class CustomPasswordValidator:
    def __init__(self, min_length=6):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _('Password must be at least %(min_length)d characters long.'),
                code='password_too_short',
                params={'min_length': self.min_length},
            )
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('Password must contain at least one uppercase letter.'),
                code='password_no_uppercase',
            )
        
        if not re.search(r'\d', password):
            raise ValidationError(
                _('Password must contain at least one number.'),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            'Your password must be at least %(min_length)d characters long and contain at least one uppercase letter and one number.'
        ) % {'min_length': self.min_length}

    def __call__(self, password):
        return self.validate(password) 