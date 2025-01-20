from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command

class StockLocation(models.Model):
    _inherit = 'stock.location'

    product_expense_account = fields.Boolean('Utilizar cuenta de gastos.',
                                             help='Utilizar cuenta de gastos de la categoria de los productos para los asientos contables.')

