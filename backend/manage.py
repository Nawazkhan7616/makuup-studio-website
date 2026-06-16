#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

# ════════════════════════════════════════════════════════════════════════════
# SSL patch — must come before Django starts (before mongoengine.connect()).
#
# Problem: Python 3.14 + OpenSSL 3.x sets SECLEVEL=2 and strict TLS options
#          that cause MongoDB Atlas to reply TLSV1_ALERT_INTERNAL_ERROR.
#
# Fix: Import pymongo's pool module early, then replace its module-level
#      `get_ssl_context` binding. Python looks up module globals at CALL TIME
#      (late binding), so this patch takes effect for every future connection.
# ════════════════════════════════════════════════════════════════════════════
import ssl as _ssl

def _atlas_ssl_ctx(*args, **kwargs):
    """SSL context compatible with MongoDB Atlas on Python 3.14."""
    ctx = _ssl.SSLContext(_ssl.PROTOCOL_TLS_CLIENT)
    # Must disable check_hostname before setting CERT_NONE
    try:
        ctx.check_hostname = False
    except Exception:
        pass
    try:
        ctx.verify_mode = _ssl.CERT_NONE
    except Exception:
        pass
    # Allow legacy TLS renegotiation (Atlas needs this on Python 3.14 OpenSSL 3.x)
    if hasattr(_ssl, 'OP_LEGACY_SERVER_CONNECT'):
        try:
            ctx.options |= _ssl.OP_LEGACY_SERVER_CONNECT
        except Exception:
            pass
    # Lower cipher security level — fixes TLSV1_ALERT_INTERNAL_ERROR
    try:
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
    except Exception:
        pass
    return ctx

# Pre-import pymongo modules so we can patch their module-level bindings.
# Late binding means get_ssl_context(...) calls look up the name in the
# caller module's globals at call time — so replacing the binding here works.
#
# Modules that import get_ssl_context (found via grep):
#   - pymongo.client_options  (line 35 — main connection path)
#   - pymongo.encryption      (line 74 — client-side field level encryption)
try:
    import pymongo.ssl_support as _ssl_support
    import pymongo.client_options as _client_options
    _ssl_support.get_ssl_context = _atlas_ssl_ctx
    _client_options.get_ssl_context = _atlas_ssl_ctx
    try:
        import pymongo.encryption as _enc
        if hasattr(_enc, 'get_ssl_context'):
            _enc.get_ssl_context = _atlas_ssl_ctx
    except Exception:
        pass
except Exception as _e:
    import warnings
    warnings.warn(f"SSL pre-patch failed: {_e}")
# ════════════════════════════════════════════════════════════════════════════

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'makuup.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
