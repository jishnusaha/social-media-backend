from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_not_empty(value):
    if value == "":
        raise ValidationError(_("This field cannot be blank."), code="invalid")
