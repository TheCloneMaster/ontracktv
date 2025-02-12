# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################


{
    "name": "Sale Fix Discount Per Line Setup",
    "version": "17.0.1.0.0",
    "summary": "Allows you to manage sale discounts per line in various ways.",
    "description": "This module enhances Odoo's discount management by introducing flexible line-level discounts. Discounts can be applied in three ways: as a percentage of the line total, a fixed amount discount on the line total, or a per-unit discount.",
    'company': 'EKIKA CORPORATION PRIVATE LIMITED',
    'author': 'EKIKA',
    'website': 'https://ekika.co',
    "category": "Sales,Tutorial,Extra Tools",
    'license': 'OPL-1',
    "depends": ["sale"],
    "data": [
        'views/res_config_settings_views.xml',
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    'auto_install': True,
    'price': 0,
    'currency': 'EUR',
}
