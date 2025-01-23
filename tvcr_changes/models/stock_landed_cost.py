from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def get_valuation_lines(self):
        self.ensure_one()
        lines = []

        for move in self._get_targeted_move_ids():
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            if move.product_id.cost_method not in ('fifo', 'average') or move.state == 'cancel' or not move.quantity:
                continue
            qty = move.product_uom._compute_quantity(move.quantity, move.product_id.uom_id)
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': qty,
                'former_cost': sum(move.stock_valuation_layer_ids.mapped('value')),
                'weight': move.product_id.weight * qty,
                'volume': move.product_id.volume * qty,
                'move_name': move.description_picking
            }
            lines.append(vals)

        if not lines:
            target_model_descriptions = dict(self._fields['target_model']._description_selection(self.env))
            raise UserError(_("You cannot apply landed costs on the chosen %s(s). Landed costs can only be applied for products with FIFO or average costing method.", target_model_descriptions[self.target_model]))
        return lines

class StockValuationAdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    move_name = fields.Char('Descripcion de Traslado')

    @api.depends('cost_line_id.name', 'product_id.code', 'product_id.name', 'move_name')
    def _compute_name(self):
        for line in self:
            name = '%s - ' % (line.cost_line_id.name if line.cost_line_id else '')
            line.name = name + (line.move_name or line.product_id.code or line.product_id.name or '')