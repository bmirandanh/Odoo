{
    'name': 'FGMED WhatsApp',
    'version': '0.0.0.1',
    'summary': 'Módulo para cadastramento e disparo de WhatsApp',
    'category': 'Tools',
    'author': 'Bruno Miranda',
    
    'depends': ['base', 'web', 'crm'],
    
    'data': [
        'views/whatsviews.xml',
        'views/data.xml',
    ],
            
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
