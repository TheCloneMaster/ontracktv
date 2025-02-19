# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _

class HideMenuRole(models.Model):
    _inherit = 'res.users.role'

    admin_role = fields.Boolean('Rol de Administracion')
    menu_ids = fields.Many2many('ir.ui.menu', 'Menus', domain=[('parent_id', '=', False), ('id', 'not in', [1,81])])

    def write(self, vals):
        res = super().write(vals)
        if 'menu_ids' in vals:
            for m in self.menu_ids:
                m.write({
                    'role_ids': [(4, self.id)]
                })
        return res

    def _assign_admin_role(self):
        self.ensure_one()
        menu_ids = self.env['ir.ui.menu'].search([('parent_id', '=', False), ('id', 'not in', [1,81]), ('active', '=', True)])
        for m in menu_ids:
             m.write({
                'role_ids': [(4, self.id)],
            })
        self.write({
            'menu_ids': [(6, 0, menu_ids.ids)]
        })
        self.admin_role = True

    def _reset_menu_roles(self):
        menus = self.env['ir.ui.menu'].search([('parent_id', '=', False),('role_ids', '!=', False)])
        roles = self.search([])
        for m in menus:
            m.role_ids = False
        for r in roles:
            r.admin_role = False
            r.menu_ids = False


