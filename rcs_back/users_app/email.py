from djoser.email import ActivationEmail


class EmailConfirmation(ActivationEmail):
    """Email для подтверждения почты с изменённым текстом"""
    template_name = "email_confirmation.html"
