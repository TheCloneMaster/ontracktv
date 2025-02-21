# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models


class BudgetLines(models.Model):
    """Inherited to add extra fields"""
    _inherit = "crossovered.budget.lines"

    alert_type = fields.Selection(
        [('warning', 'Warning Message'), ('ignore', 'Ignore'),
         ('stop', 'Stop/ Restrict')], string="Alert Type", help="Type of Alert")
    remaining_amount = fields.Monetary(
        compute='_compute_remaining_amount', string='Total Restante',
        help="Amount you have still available.")

    def _compute_remaining_amount(self):
        for line in self:
            line.remaining_amount = line.planned_amount - line.practical_amount
