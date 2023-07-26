{
    'name': 'Validação de Ordem de Venda',
    'version': '1.0',
    'summary': 'Módulo de padronização de ordem de venda ',
    'description': 'Este módulo adiciona uma padronização para que as vendas ao serem criadas, confiram o endereço do contato',
    'category': 'CRM - Contatos',
    'author': 'Bmiranda',
    'depends': [
    'base', 
    'crm',
    'account',
    'base_address_city',
    'l10n_br_base',
    'sale_management',
    'l10n_br_base_address',
     ],
    'data': [
    ],
    'installable': True,
    'auto_install': False,
}
