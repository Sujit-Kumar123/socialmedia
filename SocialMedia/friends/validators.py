from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

class CustomEmailValidator:
    def __call__(self, value):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise ValidationError(
                _('Invalid email format: %(value)s'),
                params={'value': value},
            )
