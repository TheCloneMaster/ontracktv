# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

from . import models

def update_existing_discount_values(env):
    env.cr.execute("""
        UPDATE sale_order_line
        SET 
            advance_discount = discount,
            discount_conf_id = (SELECT id FROM advance_discount_selection WHERE value = 'percentage_discount')
        WHERE discount > 0.0
    """)