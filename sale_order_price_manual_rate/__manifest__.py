# Copyright 2025 Mario Arias <support@cysfuturo.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Apply exchange factor to prices in sale order lines",
    "summary": "Recalculate prices on sale order lines",
    "version": "17.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "CYSFuturo",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale"],
    "data": ["views/sale_order_view.xml"],
}
