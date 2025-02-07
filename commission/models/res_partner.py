# Copyright 2018 Tecnativa - Ernesto Tejeda
# Copyright 2016-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ResPartner(models.Model):
    """Add some fields related to commissions"""

    _inherit = "res.partner"

    agent_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="partner_agent_rel",
        column1="partner_id",
        column2="agent_id",
        domain=[("agent", "=", True)],
        readonly=False,
        string="Agencias permitidas",
    )
    # Fields for the partner when it acts as an agent
    comision_sobre_canje = fields.Boolean(string="Comisión sobre canje")
    agent = fields.Boolean(
        string="Es Agencia",
        help="Marque este campo si el socio es una agencia.",
    )
    agent_type = fields.Selection(
        selection=[("agent", "Agencia Externa")],
        string="Tipo",
        default="agent",
    )
    # commission_id = fields.Many2one(
    #     string="Comisión",
    #     comodel_name="commission",
    #     help="Esta es la comisión por defecto usada en las ventas donde este "
    #     "agente se asigna. Puede ser cambiada en cada operación si es "
    #     "necesario.",
    # )
    settlement = fields.Selection(
        selection=[
            ("biweekly", "Bi-semanal"),
            ("monthly", "Mensual"),
            ("quaterly", "Trimestral"),
            ("semi", "Semestral"),
            ("annual", "Anual"),
        ],
        string="Período de cálculo",
        default="monthly",
    )

    @api.model
    def _commercial_fields(self):
        """Add agents to commercial fields that are synced from parent to childs."""
        res = super()._commercial_fields()
        res.append("agent_ids")
        return res
