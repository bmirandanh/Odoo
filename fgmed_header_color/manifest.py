# -*- coding: utf-8 -*-
{
    'name': 'Footer Background Color',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Inserts dynamic CSS with footer background color',
    'description': """
Inserts dynamic CSS with footer background color
==============================================

This module inserts dynamic CSS into the Odoo backend that allows for setting the background color of the footer. The color can be set in the Odoo backend by going to "Website > Configuration > Footer Background Color".
""",
    'depends': ['base', 'web', 'website'],
    'data': [
        'views/assets.xml',
        'views/footer_config_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
