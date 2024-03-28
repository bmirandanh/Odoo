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
        'views/auto_cron.xml',

        'views/wizards.xml',
        'security/ir.model.access.xml',
        'security/ir.model.access.csv',
        'views/cursos_e_matriculas.xml',
        'views/confirmacao_disciplina.xml',
        'views/quadro_de_informacoes.xml',
        'views/assets.xml',
        'views/campo_aluno.xml',        
    ],
    'installable': True,
    'auto_install': False,
}
