from odoo import api, fields, models, tools, _
from odoo.tools import format_date, formatLang
from collections import defaultdict, Counter


class StockValuationAdjustmentMatrix(models.Model):
    _name = 'stock.valuation.adjustment.matrix'

    x_axis = fields.Char(store=True)
    y_axis = fields.Char(store=True)
    cell = fields.Monetary(store=True)
    currency_id = fields.Many2one('res.currency')

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    matrix_lines = fields.Many2many('stock.valuation.adjustment.matrix', compute='_compute_matrix_values')

    @api.depends('valuation_adjustment_lines')
    def _compute_matrix_values(self):
        for i in self:
            if i.valuation_adjustment_lines and i.picking_ids:
                matrix_vals = []
                for line in i.valuation_adjustment_lines:
                    y_axis = line.move_id.purchase_line_id.name
                    currency = line.currency_id.id
                    vals = {
                        'x_axis': 'Valor original',
                        'y_axis': y_axis,
                        'cell': line.former_cost,
                        'currency_id': currency
                    }
                    matrix_vals.append((0, 0, vals))
                    vals = {
                        'x_axis': line.cost_line_id.name,
                        'y_axis': y_axis,
                        'cell': line.additional_landed_cost,
                        'currency_id': currency
                    }
                    matrix_vals.append((0, 0, vals))

                # Agrupar por axis Y (Producto) y sumar los valores
                grouped = defaultdict(list)
                for _, _, dictionary in matrix_vals:
                    y_axis_value = dictionary.get('y_axis')
                    if y_axis_value:
                        grouped[y_axis_value].append(dictionary)

                for key in grouped:
                    cell_counts = Counter(d.get('cell', 0) for d in grouped[key])
                    total_cell_value = 0
                    seen_valor_original = False
                    for d in grouped[key]:
                        if d['x_axis'] == 'Valor original' and not seen_valor_original:
                            total_cell_value += d['cell']
                            seen_valor_original = True
                        elif d['x_axis'] != 'Valor original':
                            total_cell_value += d['cell']
                    currency_id = grouped[key][0].get('currency_id')

                    vals = {
                        'x_axis': 'Total',
                        'y_axis': key,
                        'cell': total_cell_value,
                        'currency_id': currency_id,
                    }
                    matrix_vals.append((0, 0, vals))

                # Asignar valores a many2many
                i.matrix_lines = matrix_vals
            else:
                i.matrix_lines = False

class StockValuationAdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    @api.depends('cost_line_id.name', 'product_id.code', 'product_id.name', 'move_id')
    def _compute_name(self):
        for line in self:
            description = line.move_id.description_picking
            name = '%s - ' % (line.cost_line_id.name if line.cost_line_id else '')
            line.name = name + (description or line.product_id.code or line.product_id.name or '')
