{
    'name': 'TAG em produtos',
    'version': '1.0',
    'summary': 'Módulo de Validação do cadastro do telefone',
    'description': 'Criação do campo de TAG em produtos',
    'category': 'CRM - Produtos',
    'author': 'Bmiranda',
    'depends': [
    'base', 
    'crm',
    'account',
    'base_address_city',
    'l10n_br_base',
    'l10n_br_base_address',
     ],
    'data': [
        'views/product_tag_menu.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
