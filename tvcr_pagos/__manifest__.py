{
    'name': 'TVCR Pagos',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Gestión de pagos para TVCR',
    'author': 'TVCR',
    'depends': ['base', 'web', 'account', 'purchase', 'stock', 'account_payment_order', 'point_of_sale'],
    'data': [
        'security/tvcr_pagos_security.xml',
        'security/ir_rule.xml',
        'views/tvcr_pagos_menu.xml',
        'views/ir_ui_menu.xml',
        'views/res_users_role.xml',
        'views/role_menu_items.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
