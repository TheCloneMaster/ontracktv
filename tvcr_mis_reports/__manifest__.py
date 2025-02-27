# -*- coding: utf-8 -*-
# © 2015-2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>

{
    'name': 'MIS - Reporte de Activos',
    'version': '17.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'MIS Report templates for the CR Trial Balance',
    'author': 'CYSFuturo',
    'website': 'http://www.cysfuturo.com',
    'depends': ['mis_builder'],
    'data': [
        'data/mis_report_data.xml',
        'data/mis.report.style.csv',
        'data/mis.report.kpi.csv',
        'data/mis.report.subkpi.csv',
        'data/mis.report.kpi.expression.csv'
        ],
    'installable': True,
}
