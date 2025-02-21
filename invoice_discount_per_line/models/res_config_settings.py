# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_invoice_discount_per_line = fields.Boolean('Discount Per Line')
    advance_percentage_discount = fields.Boolean('Percentage Discount',
                                    related='company_id.advance_percentage_discount', readonly=False)
    fix_discount_per_line = fields.Boolean('Fix Discount Per Line',
                                    related='company_id.fix_discount_per_line', readonly=False)
    fix_discount_per_unit = fields.Boolean('Fix Discount Per Unit',
                                    related='company_id.fix_discount_per_unit', readonly=False)
