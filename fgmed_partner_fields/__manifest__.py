{
    'name': 'FGMED - Campos Especiais - Parceiros',
    'version': '1.1',
    'summary': 'Cria campos próprios para FG, bem como validação de CPF/CNPJ',
    'description': 'São criados campos como RG e Órgão expedidor, Identidade profissional e Conselho de classe',
    'category': 'Contatos',
    'author': 'Bruno Miranda - David Marques',
    'depends': [
        'base',
        'account',
        'base_address_city',
        'l10n_br_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fgmed_regulators.xml',
        'views/fgmed_professions.xml',
        'views/res_partner_view.xml'
        ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
