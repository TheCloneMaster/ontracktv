# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class HideMenuRole(models.Model):
    _inherit = 'res.users.role'

    menu_ids = fields.Many2many('ir.ui.menu', 'Menus', domain=[('parent_id', '=', False), ('id', 'not in', [1,81])])

    def write(self, vals):
        res = super().write(vals)
        if 'menu_ids' in vals:
            for m in self.menu_ids:
                m.write({
                    'role_ids': [(4, self.id)]
                })
        return res

    def _reset_menu_roles(self):
        menus = self.env['ir.ui.menu'].search([('parent_id', '=', False),('role_ids', '!=', False)])
        roles = self.search([])
        for m in menus:
            m.sudo().write({'role_ids': False})
        for r in roles:
            r.sudo().write({'admin_role': False, 'menu_ids': False})
