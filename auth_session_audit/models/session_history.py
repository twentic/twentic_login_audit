from odoo import fields, models


class SessionHistory(models.Model):
    _name = 'session.history'
    _description = 'Session History'
    _order = 'login_date desc'
    _rec_name = 'user_id'

    # Disable all manual CRUD from the UI
    _log_access = True

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=True,
        ondelete='cascade',
        index=True,
    )
    login_date = fields.Datetime(
        string='Login Date',
        required=True,
        index=True,
    )
    ip_address = fields.Char(
        string='IP Address',
    )
    user_agent = fields.Char(
        string='User Agent',
    )
    location = fields.Char(
        string='Location',
        help='GeoIP-based location, if available.',
    )
    latitude = fields.Char(
        string='Latitude',
        help='GeoIP-based latitude, if available.',
    )
    longitude = fields.Char(
        string='Longitude',
        help='GeoIP-based longitude, if available.',
    )
    session_id = fields.Char(
        string='Session ID',
        index=True,
    )
