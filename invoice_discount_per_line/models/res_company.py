# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

from odoo import api, fields, models, _

class Company(models.Model):
    _inherit = 'res.company'

    advance_percentage_discount = fields.Boolean('Percentage Discount', default=True)
    fix_discount_per_line = fields.Boolean('Fix Discount Per Line', default=True)
    fix_discount_per_unit = fields.Boolean('Fix Discount Per Unit', default=True)
