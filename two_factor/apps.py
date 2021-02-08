from webauthn import webauthn
from django.apps import AppConfig
from django.conf import settings


class TwoFactorConfig(AppConfig):
    name = 'two_factor'
    verbose_name = "Django Two Factor Authentication"

    defaults = {
        'TWO_FACTOR_WEBAUTHN_TRUSTED_ATTESTATION_ROOT': webauthn.DEFAULT_TRUST_ANCHOR_DIR,
        'TWO_FACTOR_WEBAUTHN_TRUSTED_ATTESTATION_CERT_REQUIRED': True,
        'TWO_FACTOR_WEBAUTHN_SELF_ATTESTATION_PERMITTED': False,
        'TWO_FACTOR_WEBAUTHN_UV_REQUIRED': False,
        'TWO_FACTOR_WEBAUTHN_RP_NAME': None,
    }

    def ready(self):
        for name, default in self.defaults.items():
            value = getattr(settings, name, default)
            setattr(settings, name, value)

        if getattr(settings, 'TWO_FACTOR_PATCH_ADMIN', True):
            from .admin import patch_admin
            patch_admin()
