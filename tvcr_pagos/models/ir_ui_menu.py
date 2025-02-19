# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RestrictMenu(models.Model):
    _inherit = 'ir.ui.menu'

    role_ids = fields.Many2many('res.users.role')

    def _action_reset_roles(self):
        for menu in self:
            records = menu.filtered(lambda r: r.role_ids != False)
            records.role_ids = False
