{
    'name': 'Cursos e martrículas',
    'version': '1.0',
    'summary': 'Modelo de cursos e martrículas',
    'description': 'Requisições das informações da venda',
    'category': 'CRM',
    'author': 'Bmiranda',
    'depends': [
        'base', 
        'crm',
        'sale',
        'account',
    ],
    'data': [
        'views/cursos_e_matriculas.xml',
        'views/campo_aluno.xml',
        'security/ir.model.access.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
