{
    "name": "Account Payment Order BAC",
    "version": "17.0.1.0.0",
    "category": "Banking",
    "license": "AGPL-3",
    "summary": "Create payment files for BAC bank",
    "author": "Codeium",
    "depends": [
        "account_payment_order",
        "account_payment_partner"
    ],
    "data": [
        "views/account_payment_line_views.xml",
        "views/account_payment_mode_view.xml",
        "views/account_payment_order_view.xml"
    ],
    "installable": True,
}
