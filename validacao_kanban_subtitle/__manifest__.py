{
    'name': 'Validação do Kanban',
    'version': '1.0',
    'summary': 'Módulo para validar o subtitle do kanbam',
    'description': 'Este módulo adiciona uma validação de subtitle para o módulo do pipeline do Odoo poder verificar o nome do contato para realizar a substitução',
    'category': 'crm',
    'author': 'Bmiranda',
    'depends': [
        'base',
        'crm',
    ],
    'data': [
        'views/validacao_kanban_contact_name.xml',
        ],
    'installable': True,
}