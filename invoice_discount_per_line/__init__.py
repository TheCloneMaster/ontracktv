# -*- coding: utf-8 -*-
from . import models

def update_existing_discount_values(env):
    env.cr.execute("""
        UPDATE account_move_line
        SET 
            advance_discount = discount,
            discount_conf_id = (SELECT id FROM advance_discount_selection WHERE value = 'percentage_discount')
        WHERE discount > 0.0
    """)