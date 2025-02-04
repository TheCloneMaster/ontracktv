{
    "name": "Carga de Distribución Analítica",
    "version": "17.0.1.0.0",
    "category": "Accounting/Accounting",
    "summary": "Carga distribución analítica desde Excel",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/invoice_analytic_distribution_wizard_views.xml"
    ],
    "external_dependencies": {
        "python": ["xlrd"]
    },
    "application": True,
    "installable": True
}
