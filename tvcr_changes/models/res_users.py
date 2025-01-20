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

    # allowed_users = fields.Many2many('res.users', 'res_user_users_sertec_rel', 'uid', 'allowed_users', string='Talleres Permitidos')

    is_approver = fields.Boolean('Es Aprobador', default=False)
    valid_purchase_approvers = fields.Many2many('res.users', string='Aprobadores Compras', relation="user_purchase_approvers", column1="submitter", column2="approver")
    valid_expense_approvers = fields.Many2many('res.users', string='Aprobadores Gastos', relation="user_expense_approvers", column1="submitter", column2="approver")