# -*- coding: utf-8 -*-

# Actualizar el campo tax_names para los registros existentes
def update_tax_names_str(cr, registry):
    cr.execute("""
        UPDATE account_move_line
        SET tax_names = subquery.tax_names
        FROM (
            SELECT aml.id AS aml_id, string_agg(at.name, ', ' ORDER BY at.name) AS tax_names
            FROM account_move_line aml
            LEFT JOIN account_move_line_account_tax_rel aml_at ON aml.id = aml_at.account_move_line_id
            LEFT JOIN account_tax at ON aml_at.account_tax_id = at.id
            GROUP BY aml.id
        ) AS subquery
        WHERE account_move_line.id = subquery.aml_id;
    """)

from . import models
from . import wizard
from . import report
