import re
import json
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import phonenumbers
import logging
from datetime import datetime, timedelta, date
from . import api_facturae

_logger = logging.getLogger(__name__)


class PartnerElectronic(models.Model):
    _inherit = "res.partner"

    # ==============================================================================================
    #                                          PARTNER
    # ==============================================================================================

    # === Partner fields === #

    show_description = fields.Boolean(
        string="Mostrar Descripción",
        default=False
    )

    # === Customer defined XML fields === #
    other_text_expression = fields.Text( default='''
# Available variables:
#----------------------
# invoice: object containing the current invoice
# Note: returned value have to be set in the variable 'result'
#result = "<MyTag>"+invoice.ref "</MyTag>"
result=False''')


    other_content_expression = fields.Text( default='''
# Available variables:
#----------------------
# invoice: object containing the current invoice
# Note: returned value have to be set in the variable 'result'
#result = "<MyTag>"+invoice.ref "</MyTag>"
result=False''')

    # === Economic Activity fields === #

    activity_id = fields.Many2one(
        comodel_name="economic.activity",
        string="Default Economic Activity",
        context={
            'active_test': False
        }
    )
    economic_activities_ids = fields.Many2many(
        comodel_name='economic.activity',
        string='Economic Activities',
        context={
            'active_test': False
        }
    )

