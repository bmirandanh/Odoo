# -*- coding: utf-8 -*-
{
    'name': 'FGMED Canvas',
    'version': '0.0.0.3',
    'summary': 'Módulo que entrega recursos adicionais ao Canvas',
    'category': 'Tools',
    'author': 'David Marques',
    'maintainer': 'OctoCM Sistemas inteligentes',
    'company': 'OctoCM Sistemas inteligentes',
    'website': 'https://www.octocm.com',
    'depends': ['base'],
    'data': [
    'security/ir.model.access.csv',
    'views/fgmed_canvas_content.xml',
    'views/fgmed_canvas_content_vit.xml',
    'views/fgmed_canvas_courses.xml',
    'views/fgmed_canvas_authors.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
