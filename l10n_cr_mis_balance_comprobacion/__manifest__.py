# -*- coding: utf-8 -*-
# © 2015-2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>

{
    'name': 'MIS reports BC for Costa Rica',
    'version': '17.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'MIS Report templates for the CR Trial Balance',
    'author': 'CYSFuturo',
    'website': 'http://www.cysfuturo.com',
    'depends': ['mis_builder', 'l10n_cr_mis_reports'],
    'data': [
        #'data/mis.report.style.csv',
        'data/mis_report_bc.xml',
        'data/mis.report.kpi.csv',
        'data/mis.report.subkpi.csv',
        'data/mis.report.kpi.expression.csv',
        ],
    'installable': True,
}
