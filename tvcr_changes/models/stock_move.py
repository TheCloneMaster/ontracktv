from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_dest_account(self, accounts_data):
        if not self.location_dest_id.usage in ('production', 'inventory'):
            return accounts_data['stock_output'].id
        elif self.location_dest_id.product_expense_account:
            return self.product_id.categ_id.property_account_expense_categ_id.id or accounts_data['stock_output'].id
        else:
            return self.location_dest_id.valuation_in_account_id.id or accounts_data['stock_output'].id