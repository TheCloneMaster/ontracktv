# Copyright 2020 Tecnativa - Manuel Calero
# Copyright 2022 Quartile
# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class CommissionSettlement(models.Model):
    _name = "commission.settlement"
    _description = "Settlement"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char()
    total = fields.Float(compute="_compute_total", readonly=True, store=True)
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    # agent_id = fields.Many2one(
    #     comodel_name="res.partner",
    #     domain="[('agent', '=', True)]",
    #     required=True,
    # )
    # agent_type = fields.Selection(related="agent_id.agent_type")
    settlement_type = fields.Selection(
        selection=[("manual", "Manual")],
        default="manual",
        readonly=True,
        required=True,
        help="The source of the settlement, e.g. 'Sales invoice', 'Sales order', "
        "'Purchase order'...",
    )
    can_edit = fields.Boolean(
        compute="_compute_can_edit",
        help="Technical field for determining if user can edit settlements",
        store=True,
    )
    line_ids = fields.One2many(
        comodel_name="commission.settlement.line",
        inverse_name="settlement_id",
        string="Settlement lines",
    )
    state = fields.Selection(
        selection=[
            ("settled", "Settled"),
            ("cancel", "Canceled"),
        ],
        readonly=True,
        required=True,
        default="settled",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
        default=lambda self: self._default_currency_id(),
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self._default_company_id(),
        required=True,
    )

    def _default_currency_id(self):
        return self.env.company.currency_id.id

    def _default_company_id(self):
        return self.env.company.id

    # @api.depends("line_ids")
    # def _compute_total(self):
    #     for record in self:
    #         record.total = sum(record.mapped("line_ids.settled_amount"))

    @api.depends("settlement_type")
    def _compute_can_edit(self):
        for record in self:
            record.can_edit = record.settlement_type == "manual"

    def action_cancel(self):
        self.write({"state": "cancel"})

    # def _message_auto_subscribe_followers(self, updated_values, subtype_ids):
    #     res = super()._message_auto_subscribe_followers(updated_values, subtype_ids)
    #     if updated_values.get("agent_id"):
    #         res.append((updated_values["agent_id"], subtype_ids, False))
    #     return res

    def compute_settlement_lines(self):
        self.ensure_one()
        # Buscar todas las facturas en el período
        invoices = self.env['account.move'].search([
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
        ])

        commission_section_ids = self.env['commission.section'].search([])
        commission_sections = [
            (section.amount_from, section.amount_to, section.percent)
            for section in commission_section_ids
        ]
        commission_medium_ids = self.env['commission.medium'].search([])
        commission_mediums = [
            (medium.medium_code, medium.percent)
            for medium in commission_medium_ids
        ]

        # Crear diccionario para agrupar facturas por dirección de entrega
        invoices_by_agent = {}
        
        for invoice in invoices:
            # Obtener la dirección clave (parent_id de shipping o la dirección de entrega directa)
            try:
                shipping_address = invoice.partner_shipping_id
                key_address = shipping_address.parent_id and shipping_address.parent_id.id or shipping_address.id
            except Exception as e:
                _logger.error(f"Error getting shipping address for invoice {invoice.id}: {e}")
                continue

            # Calcular commission_base (monto sin impuestos de líneas no exentas de comisión)
            volumen_base = sum(
                line.price_subtotal
                for line in invoice.invoice_line_ids
                if not line.product_id.commission_free
            )
            commission_base = sum(
                line.price_subtotal
                for line in invoice.invoice_line_ids
                if not line.product_id.commission_free
            )
            
            # Agregar la factura al diccionario usando la dirección como llave
            if key_address not in invoices_by_agent:
                invoices_by_agent[key_address] = {'invoices': []}
            
            invoices_by_agent[key_address]['invoices'].append({
                'invoice': invoice,
                'invoice_amount': invoice.amount_total,
                'volumen_base': volumen_base,
                'commission_base': commission_base,
            })

        # Calcular totales por agente
        for agent in invoices_by_agent.keys():
            agent_invoices = invoices_by_agent[agent]['invoices']
            invoices_by_agent[agent].update({
                'total_amount': sum(inv['invoice_amount'] for inv in agent_invoices),
                'total_volumen_base': sum(inv['volumen_base'] for inv in agent_invoices),
                'total_commission_base': sum(inv['commission_base'] for inv in agent_invoices),
            })
            for agent_invoice in agent_invoices:
                try:
                    values = {
                        'name': agent_invoice['invoice'].name,
                        'settlement_id': self.id,
                        'company_id': agent_invoice['invoice'].company_id.id,
                        'currency_id': agent_invoice['invoice'].currency_id.id,
                        'date': agent_invoice['invoice'].invoice_date,
                        'agent_id': agent,
                        'invoice_id': agent_invoice['invoice'].id,
                        'agent_volume': invoices_by_agent[agent]['total_volumen_base'],
                        'invoice_amount': agent_invoice['invoice_amount'],
                        'commission_base': agent_invoice['commission_base'],
                    }

                                # <field name="commission_amount" sum="Monto Comisión" widget="monetary" options="{'currency_field': 'currency_id'}" />
                                # <field name="volume_amount" sum="Monto Volumen" widget="monetary" options="{'currency_field': 'currency_id'}" />
                                # <field name="pronto_pago" sum="Pronto Pago" widget="monetary" options="{'currency_field': 'currency_id'}" />



                    _logger.error(f"Settlement line values: {values}")
                    settlement_line = self.env['commission.settlement.line'].create(values)
                    _logger.error(f"Settlement line: {settlement_line}")
                except Exception as e:
                    _logger.error(f"Error creating settlement line: {e}")
            
        # return invoices_by_agent

class SettlementLine(models.Model):
    _name = "commission.settlement.line"
    _description = "Line of a commission settlement"

    name = fields.Char()
    settlement_id = fields.Many2one(
        "commission.settlement",
        readonly=True,
        ondelete="cascade",
        required=True,
    )
    date = fields.Date(
        readonly=False,
        store=True,
        required=True,
    )
    agent_id = fields.Many2one(
        comodel_name="res.partner",
        store=True,
    )
    # commission_id = fields.Many2one(
    #     comodel_name="commission",
    #     readonly=False,
    #     store=True,
    #     required=True,
    # )
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        # related="invoice_id.company_id",
        store=True,
    )
    currency_id = fields.Many2one(
        # related="invoice_id.currency_id",
        comodel_name="res.currency",
        store=True,
        readonly=True,
    )
    agent_volume = fields.Monetary(
        readonly=False, store=True
    )
    invoice_amount = fields.Monetary(
        readonly=False, store=True
    )
    commission_base = fields.Monetary(
        readonly=False, store=True
    )
    volume_amount = fields.Monetary(
        readonly=False, store=True
    )
    commission_amount = fields.Monetary(
        readonly=False, store=True
    )
    pronto_pago = fields.Monetary(
        readonly=False, store=True
    )
