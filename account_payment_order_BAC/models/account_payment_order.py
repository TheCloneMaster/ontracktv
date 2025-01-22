from odoo import models, fields, api
from datetime import datetime
import string
import re
import unicodedata


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    numero_envio = fields.Char(
        string='Número de Envío',
        readonly=True,
        copy=False,
        help='Número de envío generado desde la secuencia del modo de pago'
    )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if order.payment_mode_id and order.payment_mode_id.is_bac_method:
                order.numero_envio = order.payment_mode_id._get_next_shipping_number()
        return orders

    def generate_payment_file(self):
        """Generate the payment file for BAC bank.
        
        Returns:
            tuple: (payment file as string, filename)
        """
        self.ensure_one()
        if self.payment_mode_id.payment_method_id.code != 'BAC':
            return super().generate_payment_file()

        # Initialize variables
        content = []
        total_amount = sum(line.amount_currency for line in self.payment_line_ids)
        # journal_account = self.journal_id.bank_account_id.acc_number.replace('-', '')
        # payment_date = datetime.strptime(str(self.date_scheduled), '%Y-%m-%d').strftime('%Y%m%d')
        payment_date = self.date_scheduled.strftime('%Y%m%d')
        line_count = len(self.payment_line_ids)

        # Generate header line
        header = 'B' +\
            self.payment_mode_id.plan_number.zfill(4) +\
            self.numero_envio.zfill(5) +\
            ' ' * 20 +\
            ' ' * 5 +\
            payment_date +\
            f"{total_amount:14.2f}".replace('.', '') +\
            str(line_count).zfill(5)
        content.append(header)

        # Generate detail lines
        for idx, line in enumerate(self.payment_line_ids, 1):
            description = (self.remove_special(line.communication) or 'PAGO PROVEEDORES TELETICA')[:30].ljust(30)
            short_description = (self.remove_special(line.communication) or '').ljust(40)[:40]
            detail = (
                'T' + 
            self.payment_mode_id.plan_number.zfill(4) +
            self.numero_envio.zfill(5) +
            line.partner_bank_id.acc_number.replace('-', '')[-20:].ljust(20) + 
            str(idx).zfill(5) + 
            payment_date +
            f"{line.amount_currency:14.2f}".replace('.', '') + 
            ' ' * 5 +
            description +
            ' ' +
            self.remove_special(line.partner_id.name[:60]).ljust(60) +
            self.numero_envio.zfill(5) + str(idx).zfill(4) + 
            self.remove_special(line.name).ljust(20)[:20] + #factura  -> short description
            '2'
            )
            content.append(detail)

        # Join all lines with newline
        file_content = '\n'.join(content).encode('utf-8')
        filename = f'BAC_payment_{self.name}_{payment_date}.txt'
        
        return file_content, filename

    def remove_special(self, value):
        double_dot = value.replace(':', ' ')
        accent = (unicodedata.normalize('NFKD', double_dot)).encode('ASCII', 'ignore').decode('ASCII')
        characters =  re.sub('[^a-zA-Z0-9 \n.]', '', accent).replace('.', '')
        double_space = characters.replace('  ', ' ')
        return double_space

    def action_cancel(self):
        # Unreconcile and cancel payments
        for payment in self.payment_ids:
            if payment.state != "draft":
                payment.action_draft()
            if payment.state != "cancel":
                payment.action_cancel()
        self.write({"state": "cancel"})
        return True

