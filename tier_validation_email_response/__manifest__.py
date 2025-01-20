{
    'name': 'Tier Validation Email Response',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Handle email responses for tier validation approvals',
    'description': """
        This module extends the base_tier_validation functionality to handle
        email responses for approval notifications. When a user receives an
        approval notification email, they can respond with "aceptar" to approve
        or any other response to reject the validation request.
    """,
    'author': 'Mario Arias',
    'depends': [
        'base_tier_validation',
        'purchase',
        'mail',
    ],
    'data': [
        'datas/data.xml', 
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
