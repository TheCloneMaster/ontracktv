# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "RFQ Alternatives Report",
    "summary": "Extends the functionality of Purchase Order Alternatives to "
    "send a report to the Internal Requester.",
    "version": "17.0.1.0.0",
    "category": "Purchases",
    "author": "Mario Arias, OnTrack Consulting",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_request","purchase_requisition"],
    "data": [
        "datas/data.xml",
        "security/ir.model.access.csv",
        "views/purchase_order_views.xml",
        "wizard/rfq_send_alternatives.xml",
    ],
}
