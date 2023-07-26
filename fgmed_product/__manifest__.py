# -*- coding: utf-8 -*-
{
    'name': 'FGMED Product',
    'version': '0.0.0.3',
    'summary': 'Customizações FGMED no módulo de produtos',
    'category': 'Tools',
    'author': 'David Marques',
    'maintainer': 'OctoCM Sistemas inteligentes',
    'company': 'OctoCM Sistemas inteligentes',
    'website': 'https://www.octocm.com',
    'depends': ['base', 'product', 'account', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/fgmed_product.xml',
        'views/fgmed_crm_lead.xml',
        'views/resources.xml',
        'views/fgmed_payment_term.xml',
        'views/fgmed_product_tag.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
# Adicionar os módulos necessários para a existência deste. Ex produtos e variantes#

