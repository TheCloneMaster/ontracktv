# Copyright 2014-2016 Tecnativa - Pedro M. Baeza
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3
from odoo import fields, models


class ImportInvoiceLine(models.TransientModel):
    _name = "import.invoice.wizard"
    _description = "Import supplier invoice lines"

    supplier = fields.Many2one(
        comodel_name="res.partner",
        required=True,
    )
    invoice = fields.Many2one(
        comodel_name="account.move",
        required=True,
        domain="[('partner_id', '=', supplier), ('move_type', '=', 'in_invoice'),"
        "('state', '=', 'posted')]",
    )

    def action_import_invoice(self):
        self.ensure_one()
        dist_id = self.env.context["active_id"]
        distribution = self.env["stock.landed.cost"].browse(dist_id)
        invoice = self.invoice
        #currency_from = self.invoice.currency_id

        landed_costs_lines = invoice.line_ids.filtered(lambda line: line.is_landed_costs_line)
        cost_lines = [self.env['stock.landed.cost.lines'].with_company(self.invoice.company_id).create({
                'product_id': l.product_id.id,
                'name': l.name,
                'account_id': l.account_id.id or (l.product_id and l.product_id.product_tmpl_id.get_product_accounts()['stock_input'].id),
                'price_unit': l.price_subtotal*((l.currency_id.inverse_rate and 1/l.currency_rate) or l.currency_rate),
                'original_currency_id': l.currency_id.id,
                'currency_amount': l.price_subtotal,
                'split_method': l.product_id.split_method_landed_cost or 'equal',
                'cost_id': distribution.id,
                'invoice_id': invoice.id,
                'partner_id': invoice.partner_id.id
            }) for l in landed_costs_lines]
        distribution.write({'vendor_bill_ids': [(4, invoice.id)]})