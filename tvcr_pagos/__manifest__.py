{
    'name': 'TVCR Pagos',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Gestión de pagos para TVCR',
    'author': 'TVCR',
    'depends': ['account'],
    'data': [
        'security/tvcr_pagos_security.xml',
        'security/ir.model.access.csv',
        'views/tvcr_pagos_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
