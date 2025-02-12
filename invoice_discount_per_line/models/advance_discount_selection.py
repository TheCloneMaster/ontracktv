# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

from odoo import models, fields


class AdvanceDiscountSelection(models.Model):
    _name = 'advance.discount.selection'
    _description = 'Advance Discount Selection'

    name = fields.Char('Name', required=True)
    value = fields.Char('Value', required=True)
