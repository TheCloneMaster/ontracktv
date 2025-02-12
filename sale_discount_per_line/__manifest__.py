# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

{
    "name": "Sale Fix Discount Per Line",
    "version": "17.0.1.0.0",
    "summary": """Allows you to manage sale discounts per line in various ways.
        Odoo sale discount
        Odoo sale line discount
        Discount
        Sale Discount
        Sale Fix Discount
        Sale Fixed Discount
        Odoo Discount
        Fixed discount per line Odoo sale
        Odoo sale discount management
        Line-specific discount Odoo sales
        Odoo fixed discount configuration for sales
        Sale order item discount Odoo
        Fixed percentage discount Odoo sale
    """,
    'company': 'EKIKA CORPORATION PRIVATE LIMITED',
    'author': 'EKIKA',
    'website': 'https://ekika.co',
    "category": "Sales",
    'license': 'OPL-1',
    "depends": ['sale', 'invoice_discount_per_line', 'sale_discount_per_line_setup', 'ekika_utils'],
    "data": [
        #"data/report_sale_order_template.xml",
        "views/sale_order_views.xml",
        "views/res_config_settings_views.xml",
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    'price': 17,
    'currency': 'EUR',
    "description": "This module enhances Odoo's discount management by introducing flexible line-level discounts. Discounts can be applied in three ways: as a percentage of the line total, a fixed amount discount on the line total, or a per-unit discount.",
}
