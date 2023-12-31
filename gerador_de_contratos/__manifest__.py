{
    'name': 'Gerador de Contratos',
    'version': '1.5',
    'category': 'Productivity',
    'installable': True,
    'auto_install': False,
    
    'depends': [
        'base',
        'sale',
        'crm',
        
        ],
    
    'data': [
        'views/contract_contacts_and_contracts.xml',
        'views/contract_generator_views.xml',
        'views/contract_model_views.xml',
        'views/contract_model_list_views.xml',
        'views/create_article_view.xml',
        'views/create_article_list_view.xml',
        'security/ir.model.access.xml',
        'security/ir.model.access.csv',
        'views/gerador_manual_views.xml',
        'views/create_contract_view.xml',
        'views/contract_list_view.xml',
        'views/contract_report.xml',
        'views/contract_view.xml',
        'views/create_article_sets.xml',
        'views/contract_generator_menu.xml',
        'views/contract_qweb.xml',
        'views/contract_qweb_html.xml',     
        'views/assets.xml',
        'views/contract_simplified_view.xml'
    ],

} 
