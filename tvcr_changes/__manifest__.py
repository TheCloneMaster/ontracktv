{
    'name': 'TVCR changes',
    'version': '1.0',
    'category': 'General',
    'summary': 'General changes for TVCR',
    'depends': [
        'rfq_alternatives_report',
        'account_asset',
        'cr_electronic_invoice_qweb_fe', 
        'purchase_request',
        'hr_expense_invoice',
    ],
    'data': [
        'views/purchase_order_views.xml',
        'views/account_asset_views.xml',
        'views/res_partner_views.xml',
        #'views/helpdesk_ticket_views.xml',
        'views/res_users_views.xml',
        'views/purchase_request_views.xml',
        'views/hr_expense_sheet_views.xml',
        'views/report_sales_invoice_qweb_bayer.xml',
        'views/res_company_views.xml',
    ],
}
