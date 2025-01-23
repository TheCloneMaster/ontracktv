from odoo import api, fields, models, tools, _

class StockValuationAdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    @api.depends('cost_line_id.name', 'product_id.code', 'product_id.name', 'move_id')
    def _compute_name(self):
        for line in self:
            description = line.move_id.description_picking
            name = '%s - ' % (line.cost_line_id.name if line.cost_line_id else '')
            line.name = name + (description or line.product_id.code or line.product_id.name or '')