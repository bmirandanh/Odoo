{
    'name': 'Verificação de contatos criados no Pipeline',
    'summary': 'Adiciona validação na criação de leads',
    'description': 'Este módulo adiciona validação ao modelo de leads de Pipeline, para alertar se existe clientes já cadastrados dentro do banco de dados.',
    'version': '1.0',
    'category': 'Ferramentas',
    'author': 'Bmiranda',
    'depends': [
        'crm',
        'base',
        'web',
    ],

    'data': [
        'views/res_partner_view.xml', 
    ],

    'application': False,
}
