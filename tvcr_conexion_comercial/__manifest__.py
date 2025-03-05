{
    'name': "TVCR Conexión Comercial",
    'version': '1.0',
    'summary': "Conexión con el servicio SOAP de TVCR para órdenes de venta",
    'description': """
        Este módulo permite la integración con el servicio SOAP de TVCR para la carga automática de órdenes de venta.
    """,
    'author': 'Mario Arias - OnTrack Costa Rica',
    'category': 'Sales',
    'depends': ['sale_management', 'sale_discount_per_line'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}