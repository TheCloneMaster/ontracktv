from odoo import api, fields, models, tools, _
from odoo.tools import format_date, formatLang

class StockValuationAdjustmentMatrix(models.Model):
    _name = 'stock.valuation.adjustment.matrix'

    x_axis = fields.Char()
    y_axis = fields.Char()
    cell_value = fields.Char()

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    matrix_lines = fields.Many2many('stock.valuation.adjustment.matrix', compute='_compute_matrix_values')

    @api.depends('valuation_adjustment_lines')
    def _compute_matrix_values(self):
        for i in self:
            if i.valuation_adjustment_lines:
                matrix_vals = []

                cost_line_count = {}
                for line in i.valuation_adjustment_lines:
                    cost_line_name = line.cost_line_id.name
                    if cost_line_name not in cost_line_count:
                        cost_line_count[cost_line_name] = 1
                    else:
                        cost_line_count[cost_line_name] += 1

                for line in i.valuation_adjustment_lines:
                    cost_line_name = line.cost_line_id.name

                    if cost_line_count[cost_line_name] > 1:
                        y_axis_value = f'{cost_line_name} ({cost_line_count[cost_line_name]})'
                        cost_line_count[cost_line_name] -= 1
                    else:
                        y_axis_value = f'{cost_line_name}'

                    # Producto y linea de costo
                    vals = {
                        'x_axis': 'Producto',
                        'y_axis': y_axis_value,
                        'cell_value': line.product_id.name
                    }
                    matrix_vals.append((0, 0, vals))

                    # Costo original
                    vals2 = {
                        'x_axis': 'Costo original',
                        'y_axis': y_axis_value,
                        'cell_value': formatLang(self.env, line.former_cost, currency_obj=i.currency_id)
                    }
                    matrix_vals.append((0, 0, vals2))

                    # Nuevo valor
                    vals3 = {
                        'x_axis': 'Costo en destino adicional',
                        'y_axis': y_axis_value,
                        'cell_value': formatLang(self.env, line.additional_landed_cost, currency_obj=i.currency_id)
                    }
                    matrix_vals.append((0, 0, vals3))

                    # Costo en destino adicional
                    vals4 = {
                        'x_axis': 'Nuevo valor',
                        'y_axis': y_axis_value,
                        'cell_value': formatLang(self.env, line.final_cost, currency_obj=i.currency_id)
                    }
                    matrix_vals.append((0, 0, vals4))

                matrix_vals = sorted(matrix_vals, key=lambda x: x[2]['y_axis'])
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
