# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Budget Transfer, Account Budget Amount Transfer',
    'version': '1.0',
    'sequence': 1,
    'category': 'Accounting',
    'description':
        """
        This Module add below functionality into odoo

        - Budget Transfer from one account budget to another account budget buget postilion  budget amount alert budget amount transfer budget amount transfer account budget amount move amount budget amount adjustment move transfer

    """, 
    'summary': 'Budget Transfer from one account budget to another account budget buget postilion  budget amount alert budget amount transfer budget amount transfer account budget amount move amount budget amount adjustment move transfer',
    'depends': ['account_budget','account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'views/main_menu.xml',
        'wizard/transfer_budget.xml',
        'views/transfer_budget_history.xml'
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':19.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'pre_init_hook' :'pre_init_check',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
