{
    'name': "Importar Presupuesto desde Excel",
    'version': '1.0',
    'summary': "Importa presupuesto anual desde un archivo Excel",
    'description': """
        Este módulo permite importar el presupuesto anual desde un archivo Excel.
    """,
    'author': "Tu Nombre",
    'category': 'Accounting/Accounting',
    'depends': ['account_budget'],
    'data': [
        'wizard/import_budget_wizard_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}