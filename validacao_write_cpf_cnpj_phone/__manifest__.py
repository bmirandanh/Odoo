{
    'name': 'Validação Company Type',
    'version': '1.0',
    'summary': 'Módulo de padronização de dados de cpf/cnpj e telefone ',
    'description': 'Este módulo adiciona uma padronização de retirar os dados adicionais de formatação para telefone e cpf/cnpj',
    'category': 'Contatos',
    'author': 'Bmiranda',
    'depends': [
    'base', 
    'crm',
    'account',
    'base_address_city',
    'l10n_br_base',
     ],
    'data': [
        'views/write_view.xml'
    ],
    'js': [
        'static/src/js/partner_form.js',
        ],
    
    'installable': True,
    'auto_install': False,
}
