# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': "Account Budget Limit Alert",
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': """This Application Enables You to Issue Warnings and Alerts 
     When Purchase Orders Exceed the Budget.""",
    'description': """Empowers you to issue timely warnings and alerts 
     whenever purchase orders surpass the allocated budget, ensuring financial 
     oversight and control.""",
    'author': 'CYSFuturo S.A.',
    'company': 'CYSFuturo S.A.',
    'maintainer': 'CYSFuturo S.A.',
    'website': 'https://www.cysfuturo.com',
    'depends': ['account_budget', 'purchase'],
    'data': [
        'views/crossovered_budget_views.xml',
        'views/account_move_views.xml',
        'views/purchase_order_views.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
