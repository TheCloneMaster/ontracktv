
from xml.sax.saxutils import escape
from lxml import etree

from odoo import models, fields, api, _
from collections import defaultdict

import logging
_logger = logging.getLogger(__name__)


class AccountInvoiceElectronic(models.Model):
    _inherit = "account.move"

    # ==============================================================================================
    #                                          INVOICE
    # ==============================================================================================


    @api.depends('amount_total')
    def group_lines_by_sale_order(self):
        grouped_lines = defaultdict(list)
        for line in self.invoice_line_ids:
            for sale_line in line.sale_line_ids:
                if sale_line.order_id and sale_line.order_id.client_order_ref:  # Verificar que tenga orden de venta asociada
                    key = (line.name, sale_line.order_id.client_order_ref)
                    if key not in grouped_lines:
                        grouped_lines[key] = {
                            'descripcion': sale_line.name + ' - ' + sale_line.order_id.client_order_ref, 
                            'bruto': sale_line.price_unit, 
                            'descuento': sale_line.price_unit * line.discount / 100, 
                            'neto': sale_line.price_subtotal
                        }
                    else:
                        grouped_lines[key]['bruto'] += sale_line.price_unit
                        grouped_lines[key]['descuento'] += sale_line.price_unit * line.discount / 100
                        grouped_lines[key]['neto'] += sale_line.price_subtotal
                # else:
                #     # Si no tiene orden de venta asociada, agrupamos solo por descripcion
                #     key = (line.name, None)
                #     grouped_lines[key].append(line)
        return list(grouped_lines.values())

    @api.depends('amount_total')
    def group_lines_by_product(self):
        grouped_lines = defaultdict(list)
        for line in self.invoice_line_ids:
            key = line.product_id.id
            if key not in grouped_lines:
                grouped_lines[key] = {
                    'descripcion': line.product_id.name,
                    'cantidad': 1 ,
                    'precio_unitario': line.price_unit,
                    'bruto': line.price_unit,
                    'descuento': line.price_unit * line.discount / 100,
                    'neto': line.price_subtotal
                }
            else:
                grouped_lines[key]['cantidad'] += 1
                grouped_lines[key]['bruto'] += line.price_unit
                grouped_lines[key]['descuento'] += line.price_unit * line.discount / 100
                grouped_lines[key]['neto'] += line.price_subtotal
                # else:
                #     # Si no tiene orden de venta asociada, agrupamos solo por descripcion
                #     key = (line.name, None)
                #     grouped_lines[key].append(line)
        return list(grouped_lines.values())

    def _get_name_invoice_report(self):
        """ This method need to be inherit by the localizations if they want to print a custom invoice report instead of
        the default one. For example please review the l10n_ar module """
        self.ensure_one()
        if self.partner_id.invoice_template_id:
            return self.partner_id.invoice_template_id.xml_id
        return 'cr_electronic_invoice_qweb_fe.report_invoice_document_fecr'

