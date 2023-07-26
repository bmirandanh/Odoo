{
    'name': 'CRM Médico',
    'version': '1.0',
    'summary': 'Adiciona campo CRM no Contatos',
    'description': 'Adiciona um campo de texto CRM no módulo Contatos',
    'author': 'bmirandanh',
    'depends': ['base', 'contacts'],
    'data': [
        'views/contact_views.xml',
    ],
    'installable': True,
    'application': True,
}