{
    'name': 'Auth Session Audit',
    'version': '18.0.1.0.0',
    'summary': 'Track and audit user login sessions',
    'description': """
        Records every successful user authentication with details such as
        IP address, user agent, timestamp and optional GeoIP location.
        Provides a read-only audit trail accessible to Security Auditors.
    """,
    'category': 'Technical',
    'author': 'Twentic',
    'website': 'https://www.twentic.com/odoo',
    'depends': ['base', 'web'],
    'data': [
        'security/auth_session_audit_security.xml',
        'security/ir.model.access.csv',
        'data/res_groups_data.xml',
        'views/session_history_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
