from odoo import models, fields
import email

from html2text import html2text
import re
import logging
_logger = logging.getLogger(__name__)

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

class TierValidation(models.AbstractModel):
    _inherit = 'tier.validation'

    def _notify_review_available(self, tier_reviews):
        """method to notify when tier validation is created"""
        _logger.info('Entrando a notificar')
        for review in tier_reviews:
            if review.status == 'pending' and len(review.reviewer_ids)==1 and review.reviewer_ids.has_group('base.group_portal'):
                if review.model == 'purchase.order':
                    email_template = self.env.ref('tier_validation_email_response.email_template_purchase_order_tier_validation', raise_if_not_found=False)
                elif review.model == 'hr.expense.sheet':
                    email_template = self.env.ref('tier_validation_email_response.email_template_expense_report_tier_validation', raise_if_not_found=False)

                lang = False
                if email_template:
                    lang = email_template._render_lang(self.ids)[self.id]
                if not lang:
                    lang = get_lang(self.env).code

                _logger.info('Notificar: Enviando correo')
                email_template.with_context(type='binary',
                                            default_type='binary').send_mail(self.id,
                                            raise_exception=False,
                                            force_send=True)
        super()._notify_review_available(tier_reviews)

class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    def fetch_mail(self):
        """ WARNING: meant for cron usage only - will commit() after each email! """
        default_batch_size = 15
        additionnal_context = {
            'fetchmail_cron_running': True
        }
        MailThread = self.env['mail.thread']
        for server in self:
            if server.name  != 'erp.solicitudes@teletica.com':
                super(FetchmailServer, server).fetch_mail()
                continue

            _logger.info('start checking for new email responses on %s server %s', server.server_type, server.name)
            additionnal_context['default_fetchmail_server_id'] = server.id
            count, failed = 0, 0
            imap_server = None
            if server.server_type in ('imap', 'outlook'):
                try:
                    imap_server = server.connect()
                    # Check if Processed folder exists, if not create it
                    result, folders = imap_server.list()
                    # processed_folder_exists = False
                    # rejected_folder_exists = False
                    # for folder in folders:
                    #     if b'Processed' in folder:
                    #         processed_folder_exists = True
                    #     elif b'rejected' in folder:
                    #         rejected_folder_exists = True
                    #     if processed_folder_exists and rejected_folder_exists:
                    #         break

                    # if not processed_folder_exists:
                    #     imap_server.create('Processed')
                    
                    # if not rejected_folder_exists:
                    #     imap_server.create('Rejected')

                    imap_server.select()
                    result, data = imap_server.search(None, '(UNSEEN SINCE "22-Mar-2024")')
                    #result, data = imap_server.search(None, '(SINCE "22-Mar-2024")')
                    for num in data[0].split()[:default_batch_size]:
                        result, data = imap_server.fetch(num, '(RFC822)')
                        imap_server.store(num, '-FLAGS', '\\Seen')
                        message = data[0][1]
                        try:
                            if isinstance(message, xmlrpclib.Binary):
                                message = bytes(message.data)
                            if isinstance(message, str):
                                message = message.encode('utf-8')
                            message = email.message_from_bytes(message, policy=email.policy.SMTP)
                            msg = MailThread.with_context(**additionnal_context).message_parse(message, save_original=False)
                            result = self.process_message(msg)

                            if result == 1:
                                # Move to Processed folder
                                imap_server.copy(num, 'Inbox/Processed')
                                imap_server.store(num, '+FLAGS', '\\Deleted')
                                _logger.info("Response registered")
                            elif result == -1:
                                # Move to Rejected folder
                                imap_server.copy(num, 'Inbox/Rejected')
                                imap_server.store(num, '+FLAGS', '\\Deleted')
                                _logger.info("Error in response")
                            else:
                                imap_server.copy(num, 'Inbox/Ignored')
                                imap_server.store(num, '+FLAGS', '\\Deleted')
                                _logger.info("Ignored email")
                        except Exception:
                            _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name, exc_info=True)
                            failed += 1
                        self._cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.server_type, server.name, (count - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.server_type, server.name, exc_info=True)
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
            server.write({'date': fields.Datetime.now()})
        return True

    def process_message(self, msg):
        subject =   msg.get('subject', '')

        # Extract the email body and convert to lowercase for comparison
        msg_body = html2text(msg.get('body', ''))[:30].lower().strip()
        
        # Get the email from address to identify the reviewer
        msg_from = msg.get('from', '')  
        # email_from = msg_dict.get('email_from', '')
        if '&lt;' in msg_from and '&gt;' in msg_from:
            msg_from = re.search(r'&lt;(.+?)&gt;', msg_from).group(1)

        _logger.info("------ Process Message --------")
        _logger.info("Subject : %s " % subject)
        _logger.info("From: %s " % msg_from)
        _logger.info("To: %s " % msg.get('to', ''))

        patron = r".*(SIC|OC|AD|CH)-(\d+).::.(SOLICITUD DE APROBACIÓN).*"
        coincidencia = re.match(patron, subject)
        if coincidencia:
            prefijo = coincidencia.group(1)  # Captura el primer grupo (prefijo)
            digitos = coincidencia.group(2)  # Captura el segundo grupo (dígitos)
            documento = prefijo + '-' + digitos
        else:
            _logger.info("Sujeto no coincide con el patrón")
            return 0

        if prefijo in ('SIC', 'OC'):
            record = self.env['purchase.order'].search([('name', '=', documento)], limit=1) 
        elif prefijo in ('AD', 'CH'):
            record = self.env['hr.expense.sheet'].search([('number', '=', documento)], limit=1) 

        if not record:
            _logger.info("Registro no encontrado")
            return -1 # error en archivo

        reviewer_id = self.env['res.users'].search([('login', '=', msg_from)], limit=1)

        # Search for the pending review for this email address
        domain = [
            ('status', '=', 'pending'),
            # ('reviewer_id.email', '=', msg_from),                                
            ('model', '=', record._name),
            ('res_id', '=', record.id),
        ]
        pending_review = self.env['tier.review'].search(domain, limit=1)
        if not pending_review:
            _logger.info("Revisión no encontrada")
            return -1 # error en archivo

        if 'acept' in msg_body:
            # Approve the review
            pending_review.write({
                'status': 'approved',
                'done_by': reviewer_id.id,
                'comment': msg_body,
                'reviewed_date': fields.Datetime.now(),
            })
            # Validate the tier
            if hasattr(record, '_validate_tier'):
                record._validate_tier(pending_review)
        else:
            # Reject the review
            pending_review.write({
                'status': 'rejected',
                'done_by': reviewer_id.id,
                'comment': msg_body,
                'reviewed_date': fields.Datetime.now(),
                # 'reject_reason': email_body[:500],  # Limit the rejection reason to 500 chars
            })
            # Notify rejection
            if hasattr(record, '_notify_rejected_review'):
                record._notify_rejected_review()

        return 1


# class TierReview(models.Model):
#     _inherit = 'tier.review'

#     def _notify_review_requested(self):
#         """Override to add a more explicit message about email response."""
#         super()._notify_review_requested()
        
#         if not self.env.context.get('skip_email_response_note'):
#             # Add a note about how to respond via email
#             record = self.env[self.model].browse(self.res_id)
#             record.message_post(
#                 body="""
#                     <p>Puede responder a este correo con la palabra "aceptar" para aprobar 
#                     la solicitud, o cualquier otro texto para rechazarla.</p>
#                 """,
#                 message_type='notification',
#                 subtype_xmlid='mail.mt_note',
#             )
