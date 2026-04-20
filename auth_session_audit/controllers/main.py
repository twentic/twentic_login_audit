import logging
from datetime import datetime, timezone

from odoo import api, SUPERUSER_ID, http
from odoo.http import request
from odoo.modules.registry import Registry
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.session import Session

_logger = logging.getLogger(__name__)


class SessionAuditController(Session):
    """Extend the JSON session controller (SPA / API calls)."""

    @http.route('/web/session/authenticate', type='json', auth='none')
    def authenticate(self, db, login, password, base_location=None):
        result = super().authenticate(db, login, password, base_location=base_location)
        if request.session.uid:
            _create_session_history(db)
        return result


class HomeAuditController(Home):
    """Extend the form-based login controller (browser direct access)."""

    @http.route('/web/login', type='http', auth='none')
    def web_login(self, redirect=None, **kwargs):
        response = super().web_login(redirect=redirect, **kwargs)
        # The form POST sets session.uid on success; GET requests leave it unset.
        if request.session.uid and request.httprequest.method == 'POST':
            _create_session_history(request.session.db)
        return response


# ------------------------------------------------------------------
# Shared helper (module-level to avoid duplication)
# ------------------------------------------------------------------

def _create_session_history(db):
    """Create a session.history record for the current authenticated session.

    Uses a dedicated cursor from the Registry to avoid relying on
    request.env, which may not have a proper database context in
    auth='none' routes.
    """
    try:
        uid = request.session.uid
        ip_address = _get_client_ip()
        user_agent = _get_user_agent()
        location, latitude, longitude = _get_geoip_location()
        session_id = request.session.sid
        login_date = datetime.now(timezone.utc).replace(tzinfo=None)

        registry = Registry(db)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            env['session.history'].create({
                'user_id': uid,
                'login_date': login_date,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'location': location,
                'latitude': latitude,
                'longitude': longitude,
                'session_id': session_id,
            })
    except Exception:
        _logger.exception('auth_session_audit: failed to record session history')


def _get_client_ip():
    """Return the real client IP, respecting common reverse-proxy headers."""
    forwarded_for = request.httprequest.environ.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.httprequest.remote_addr or ''


def _get_user_agent():
    """Return the User-Agent string from the HTTP request."""
    user_agent = request.httprequest.user_agent
    return user_agent.string if user_agent else ''


def _get_geoip_location():
    """Return location data derived from GeoIP, using Odoo 18 object-style access.

    In Odoo 18, request.geoip is a GeoIP2 record object, not a dict.
    Attribute access mirrors hr_attendance's _get_geoip_response().
    """
    try:
        geoip = request.geoip
        if not geoip:
            return '', '', ''
        city = geoip.city.name or ''
        country = geoip.country.name or geoip.continent.name or ''
        location = ', '.join(p for p in [city, country] if p)
        latitude = geoip.location.latitude or ''
        longitude = geoip.location.longitude or ''
        return location, latitude, longitude
    except Exception:
        return '', '', ''
