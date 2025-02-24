# -*- coding: utf-8 -*-
# © 2015-2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>

{
    'name': 'MIS reports for France',
    'version': '17.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'MIS Report templates for the CR P&L and Balance Sheets',
    'author': 'CYSFuturo, Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.cysfuturo.com',
    'depends': ['mis_builder', 'l10n_cr'],
    'data': [
        #'data/mis_report_styles.xml',
        'data/mis.report.style.csv',
        'data/mis_report_pl.xml',
        'data/mis_report_bs.xml',
        'data/mis.report.kpi.csv',
        ],
    'installable': True,
}
