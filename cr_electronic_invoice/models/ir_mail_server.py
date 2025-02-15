# -*- coding:utf-8 -*-

import email
import base64
import pathlib

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

from lxml import etree
from datetime import datetime
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, pycompat
from odoo.tests.common import Form
from . import api_facturae

import logging
_logger = logging.getLogger(__name__)
MAX_POP_MESSAGES = 10
MAIL_TIMEOUT = 60


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    def fetch_mail(self):
        """ WARNING: meant for cron usage only - will commit() after each email! """
        default_batch_size = 10
        additionnal_context = {
            'fetchmail_cron_running': True
        }
        MailThread = self.env['mail.thread']
        invoice_load_servers = [company.import_bill_mail_server_id for company in self.env['res.company'].search([('import_bill_automatic', '=', True)])]
        for server in self:
            if server not in invoice_load_servers:
                super(FetchmailServer, server).fetch_mail()
                continue

            _logger.info('start checking for new emails on %s server %s', server.server_type, server.name)
            additionnal_context['default_fetchmail_server_id'] = server.id
            count, failed = 0, 0
            imap_server = None
            if server.server_type in ('imap', 'outlook'):
                try:
                    errors_warnings = []
                    imap_server = server.connect()
                    # Check if Processed folder exists, if not create it
                    result, folders = imap_server.list()
                    processed_folder_exists = False
                    for folder in folders:
                        if b'Processed' in folder:
                            processed_folder_exists = True
                            break
                    if not processed_folder_exists:
                        imap_server.create('Processed')
                    
                    imap_server.select()
                    result, data = imap_server.search(None, '(UNSEEN SINCE "22-Mar-2024")')
                    #result, data = imap_server.search(None, '(SINCE "22-Mar-2024")')
                    for num in data[0].split()[:default_batch_size]:
                        result, data = imap_server.fetch(num, '(RFC822)')
                        imap_server.store(num, '-FLAGS', '\\Seen')
                        message = data[0][1]
                        try:
                            ##res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, data[0][1], save_original=server.original, strip_attachments=(not server.attach))
                            if isinstance(message, xmlrpclib.Binary):
                                message = bytes(message.data)
                            if isinstance(message, str):
                                message = message.encode('utf-8')
                            ##extract = getattr(email, 'message_from_bytes', email.message_from_string)
                            ##msg_txt = extract(message)
                            # parse the message, verify we are not in a loop by checking message_id is not
                            # duplicated
                            ##msg = MailThread.with_context(**additionnal_context).message_parse(msg_txt,
                            #                                                                    save_original=False)
                            message = email.message_from_bytes(message, policy=email.policy.SMTP)
                            msg = MailThread.with_context(**additionnal_context).message_parse(message, save_original=False)
                            # Fixing --> Save Original : False --> No store Content On Odoo
                            _logger.info("------ Process Message --------")
                            _logger.info("Subject : %s " % msg.get('subject', ''))
                            _logger.info("From: %s " % msg.get('from', ''))
                            _logger.info("To: %s " % msg.get('to', ''))
                            result, warning_messages = self.create_invoice_with_attamecth(msg)
                            if result and not isinstance(result, bool):
                                # Move to Processed folder
                                imap_server.copy(num, 'Processed')
                                imap_server.store(num, '+FLAGS', '\\Deleted')
                                _logger.info("Invoice created correctly %s", str(result))
                            elif result:
                                # Move to Processed folder
                                errors_warnings.append(f"Repeated Invoice in email {msg.get('subject', '')}")
                                errors_warnings.append(f"From: {msg.get('from', '')}")
                                errors_warnings += warning_messages
                                imap_server.copy(num, 'Processed')
                                imap_server.store(num, '+FLAGS', '\\Deleted')
                                _logger.info("Repeated Invoice")
                            else:
                                errors_warnings.append(f"Ignored email {msg.get('subject', '')}")
                                errors_warnings.append(f"From: {msg.get('from', '')}")
                                errors_warnings += warning_messages
                                imap_server.copy(num, 'Inbox/Ignored')
                                imap_server.store(num, '+FLAGS', '\\Deleted')
                                _logger.info("Ignore email")
                        except Exception:
                            errors_warnings.append(f"Failed to process email {msg.get('subject', '')}")
                            errors_warnings.append(f"From: {msg.get('from', '')}")
                            errors_warnings += warning_messages
                            imap_server.copy(num, 'Inbox/Failed')
                            imap_server.store(num, '+FLAGS', '\\Deleted')
                            _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name, exc_info=True)
                            failed += 1
                        self._cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.server_type, server.name, (count - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.server_type, server.name, exc_info=True)
                finally:
                    if errors_warnings:
                        email_body = '\n'.join(errors_warnings)
                        server_saliente_id = self.env['ir.mail.server'].search([('name', '=', 'erp.facturas@teletica.com')], limit=1)
                        self.env['mail.mail'].create({
                            'subject': 'Detalle de errores cargando correos facturación electrónica',
                            'body_html': f'<pre>{email_body}</pre>',
                            'email_to': 'mi.fernandez@teletica.com,moises.murillo@teletica.com',
                            'email_from': 'erp.facturas@teletica.com',
                            'smtp_server_id': server_saliente_id.id  # ID del servidor saliente que quieres usar
                        }).send()
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
            server.write({'date': fields.Datetime.now()})
        return True

    def get_bill_exist_or_false(self, electronic_number):
        domain = [('number_electronic', '=', electronic_number)]
        return self.env['account.move'].search(domain, limit=1)

    def create_ir_attachment_invoice(self, invoice, attach, mimetype):
        if isinstance(attach.content, bytes):
            datas = base64.b64encode(attach.content)
        elif isinstance(attach.content, str):
            datas = base64.b64encode(attach.content.encode())
        return self.env['ir.attachment'].create({
            'name': attach.fname,
            'type': 'binary',
            'datas': datas,
            'res_model': 'account.move',
            'res_id': invoice.id,
            'mimetype': mimetype
        })

    def create_invoice_with_attamecth(self, msg):
        result = False
        pending_xml_responses = {}
        extra_files = {}
        processed_docs = {}
        warning_messages = []

        for attach in msg.get('attachments'):
            file_name = attach.fname or 'item.ignore'
            file_type = pathlib.Path(file_name.upper()).suffix
            try:
                if isinstance(attach.content, bytes):   
                    attach_content = attach.content
                else:
                    attach_content = attach.content.encode()
            except Exception as e:
                message = f'Error reading attachment {file_name}: {e}'
                warning_messages.append(message)
                _logger.info(message)
                continue

            if file_type == '.XML':
                    _logger.info('XML attachment = %s', file_name)
                    try:
                        invoice_xml = etree.fromstring(attach_content)
                    except Exception as e:
                        message = f'Error parsing attachment {file_name}: {e}'
                        warning_messages.append(message)
                        _logger.info(message)
                        continue

                    namespaces = invoice_xml.nsmap
                    inv_xmlns = namespaces.pop(None)
                    namespaces['inv'] = inv_xmlns

                    document_type = re.search(
                        'FacturaElectronica|NotaCreditoElectronica|'
                        'NotaDebitoElectronica|TiqueteElectronico|MensajeHacienda',
                        invoice_xml.tag).group(0)
                    
                    # if document_type == 'TiqueteElectronico' or document_type == 'NotaDebitoElectronica':
                    # if document_type == 'TiqueteElectronico':
                    #     message = "Warning: This is a TICKET only invoices are valid for taxes"
                    #     warning_messages.append(message)
                    #     _logger.info(message)
                    #     #continue
                    # # Check Exist
                    electronic_number = invoice_xml.xpath("inv:Clave", namespaces=namespaces)[0].text
                    exist_invoice = self.get_bill_exist_or_false(electronic_number)
                    processed_docs[electronic_number] = exist_invoice

                    if document_type == 'MensajeHacienda':
                        if exist_invoice:
                            if not exist_invoice.has_ack:
                                attachment_id = self.create_ir_attachment_invoice(exist_invoice, attach,
                                                                                  'application/xml')
                                exist_invoice.message_post(attachment_ids=[attachment_id.id])
                                exist_invoice.has_ack = True
                                _logger.info('ACK loaded in existing Invoice: %s', electronic_number)
                                result = exist_invoice
                            else:
                                message = 'ACK already registered in existing Invoice: ' + electronic_number + ', ignoring'
                                #warning_messages.append(message)
                                _logger.info(message)
                                result = True
                        else:  #should keep track of pending ACKs to be loaded
                            pending_xml_responses[electronic_number] = attach
                        continue
                    if document_type in ('FacturaElectronica', 'NotaCreditoElectronica', 'NotaDebitoElectronica', 'TiqueteElectronico') \
                        and exist_invoice:
                        message = 'Duplicated Document (' + electronic_number + '), ignoring'
                        warning_messages.append(message)
                        _logger.info(message)
                        result = True
                        continue

                    if document_type in ('FacturaElectronica', 'NotaDebitoElectronica', 'TiqueteElectronico'):
                        type_invoice = 'in_invoice'
                    elif document_type == 'NotaCreditoElectronica':
                        type_invoice = 'in_refund'
                    else:
                        message = 'The electronic receipt is unknown, it will simply be ignored'
                        warning_messages.append(message)
                        _logger.info(message)
                        result = True
                        continue

                    receptor = invoice_xml.xpath("inv:Receptor/inv:Identificacion/inv:Numero", namespaces=namespaces)[0].text
                    receiver_company_id = self.env['res.company'].search([('vat', '=', receptor),('import_bill_automatic', '=', True)], limit=1)
                    if not receiver_company_id: #  or not receiver_company_id.import_bill_automatic
                        message = 'Company with VAT ' + receptor + ' is not configured for automatic bill import'
                        warning_messages.append(message)
                        _logger.info(message)
                        continue
                    purchase_journal = receiver_company_id.import_bill_journal_id
                    self = self.with_context(default_journal_id=purchase_journal.id,
                                             default_type=type_invoice, type=type_invoice, journal_type='purchase')
                    invoice = self.env['account.move'].create({
                      'move_type': type_invoice,
                      'company_id': receiver_company_id.id
                    })

                    _logger.info("Document %s created: %s", document_type, invoice)
                    invoice.fname_xml_supplier_approval = attach.fname
                    #_logger.info("SIT s attach_content =purchase_journal %s",attach_content)
                    invoice.xml_supplier_approval = base64.b64encode(attach_content)

                    default_account = purchase_journal.expense_account_id
                    if default_account:
                        load_lines = purchase_journal.load_lines
                    else:
                        default_account = self.env['ir.config_parameter'].sudo().get_param('expense_account_id')
                        load_lines = bool(self.env['ir.config_parameter'].sudo().get_param('load_lines'))

                    default_analytic_account = purchase_journal.expense_analytic_account_id
                    if not default_analytic_account:
                        default_analytic_account = invoice.env['ir.config_parameter'].sudo().get_param('expense_analytic_account_id')

                    default_product = purchase_journal.expense_product_id.id
                    if not default_product:
                        default_product = self.env['ir.config_parameter'].sudo().get_param('expense_product_id')

                    importa_xml = api_facturae.load_xml_data(invoice, load_lines, default_account,
                                                            default_product,
                                                            default_analytic_account, 
                                                            interactive=False)

                    if importa_xml == -1:
                        invoice.unlink()
                    processed_docs[electronic_number] = invoice
                    result = invoice

                #except Exception as e:
                #    _logger.info("This XML file %s is not XML-compliant. Error: %s", attach.fname, e)
                #    continue
            elif file_type == '.PDF':
                extra_files[file_name] = attach
                _logger.debug("Pending PDF to process: %s", file_name)
        # Try to process pending ACKs
        for number_electronic, attach in list(pending_xml_responses.items()):
            doc = processed_docs.get(number_electronic)
            if doc:
                attachment_id = self.create_ir_attachment_invoice(doc, attach,
                                                                    'application/xml')
                doc.message_post(attachment_ids=[attachment_id.id])
        
        # Load PDFs
        if len(processed_docs)==1:
            for file_name, attach in list(extra_files.items()):
                num, doc = list(processed_docs.items())[0]
                if doc:
                    attachment_id = self.create_ir_attachment_invoice(doc, attach,
                                                                    'application/pdf')
                    doc.message_post(attachment_ids=[attachment_id.id])
        elif len(processed_docs)==0 and extra_files:
            _logger.debug("PDF files not processed: %s. No related document", extra_files)
        else:
            _logger.debug("PDF files not processed: %s. Too many documents", extra_files)
        return result, warning_messages
