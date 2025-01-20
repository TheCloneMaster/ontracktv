# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command

_logger = logging.getLogger(__name__)

class Users(models.Model):
    """ User class. A res.users record models an OpenERP user and is different
        from an employee.

        res.users class now inherits from res.partner. The partner model is
        used to store the data related to the partner: lang, name, address,
        avatar, ... The user model is now dedicated to technical data.
    """
    _inherit = "res.users"

    allowed_users = fields.Many2many('res.users', 'res_user_users_sertec_rel', 'uid', 'allowed_users', string='Talleres Permitidos')
