# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RestrictMenu(models.Model):
    _inherit = 'ir.ui.menu'

    role_ids = fields.Many2many('res.users.role')
