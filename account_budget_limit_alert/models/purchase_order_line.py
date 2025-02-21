# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    analytic_json = fields.Json('Analytic JSON', compute='_compute_analytic_json', store=True)
    is_above_budget = fields.Boolean('Is Above Budget', compute='_compute_above_budget')
    budget_line_ids = fields.One2many('crossovered.budget.lines', compute='_compute_budget_line_ids', string='Budget Lines')

    @api.depends('analytic_distribution')
    def _compute_analytic_json(self):
        for line in self:
            distribution = []
            line_account_id = line.product_id.property_account_expense_id.id or line.product_id.categ_id.property_account_expense_categ_id.id
            for analytic_account_ids, percentage in (line.analytic_distribution or {}).items():
                dist_dict = {'rate': float(percentage) / 100}
                for analytic_account in self.env['account.analytic.account'].browse(map(int, analytic_account_ids.split(","))).exists():
                    # root_plan_column = analytic_account.root_plan_id._column_name()
                    dist_dict['analytic_account_id'] = analytic_account.id
                    dist_dict['general_budget_id'] = line_account_id
                distribution.append(dist_dict)
            line.analytic_json = distribution

    @api.depends('analytic_distribution')
    def _compute_budget_line_ids(self):
        def get_domain(line):
            if line.analytic_json and line.product_qty - line.qty_received > 0:
                for json in line.analytic_json:
                    return tuple([
                        # ('budget_analytic_id', 'any', (
                        #     ('budget_type', '!=', 'revenue'),
                        #     ('state', '=', 'confirmed'),
                        # )),
                        ('date_from', '<=', line.order_id.date_order),
                        ('date_to', '>=', line.order_id.date_order),
                        ('general_budget_id.account_ids', 'in', json.get('general_budget_id',False)),
                        ('analytic_account_id', '=', json.get('analytic_account_id',False))
                    ])

        for domain, lines in self.grouped(get_domain).items():
            lines.budget_line_ids = bool(domain) and self.sudo().env['crossovered.budget.lines'].search(list(domain))

    @api.depends('budget_line_ids', 'price_unit', 'product_qty', 'qty_invoiced')
    def _compute_above_budget(self):
        for line in self:
            uncommitted_amount = 0
            if line.order_id.state not in ('purchase', 'done'):
                uncommitted_amount = line.price_unit * (line.product_qty - line.qty_invoiced)
            line.is_above_budget = any(budget.practical_amount + uncommitted_amount > budget.planned_amount 
                for budget in line.budget_line_ids)
