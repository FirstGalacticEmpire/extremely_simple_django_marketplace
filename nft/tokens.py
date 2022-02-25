from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

# https://stackoverflow.com/questions/59193514/importerror-cannot-import-name-six-from-django-utils
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return text_type(user.pk)


account_activation_token = TokenGenerator()
