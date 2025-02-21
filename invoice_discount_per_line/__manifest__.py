# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

{
    "name": "Invoice Fix Discount Per Line",
    "version": "17.0.1.0.0",
    'summary': """Allows you to manage discounts per line in various ways.
        Odoo invoice discount
        Odoo invoice line discount
        Discount
        Invoice Discount
        Invoice Fix Discount
        Invoice Fixed Discount
        Odoo Discount
        Fixed discount per line Odoo
        Odoo invoice discount management
        Line-specific discount Odoo
        Invoice item discount Odoo
        Odoo invoice discount customization
        Fixed percentage discount Odoo
    """,
    'company': 'EKIKA CORPORATION PRIVATE LIMITED',
    'author': 'EKIKA',
    'website': 'https://ekika.co',
    "category": "Accounting",
    'license': 'OPL-1',
    "depends": ['base', 'account', 'ekika_utils'],
    'post_init_hook': 'update_existing_discount_values',
    "data": [
        "security/ir.model.access.csv",
        "data/advance_discount_selection.xml",
        #"data/report_invoice_template.xml",
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
    ],
    'images': ['static/description/banner.gif'],
    "installable": True,
    'price': 17,
    'currency': 'EUR',
    "description": "This module enhances Odoo's discount management by introducing flexible line-level discounts. Discounts can be applied in three ways: as a percentage of the line total, a fixed amount discount on the line total, or a per-unit discount.",
}
