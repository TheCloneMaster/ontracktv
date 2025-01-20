from odoo import Command,_, api, fields, models
from odoo.exceptions import UserError
import logging
import traceback

# Obtén o crea un objeto Logger
_logger = logging.getLogger(__name__)

class Expense(models.Model):
    _inherit = "hr.expense"


    @api.depends("invoice_id", "tax_ids", "additional_user_ids")
    def _compute_total_amount_currency(self):
        return super(Expense, self)._compute_total_amount_currency()


class ExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    valid_expense_approvers = fields.Many2many(
        'res.users',
        related='create_uid.valid_expense_approvers',
        string='Valid Expense Approvers'
    )

    tier_validation_approver = fields.Many2one(
        'res.users',
        string="Aprobador",
        # required=True,
        domain="[('id', 'in', valid_expense_approvers)]"
    )

    def write(self, vals):
        if 'state' in vals:
            estado = vals['state']
            if estado == 'done':
                _logger.error(f"New State: {estado}")
                _logger.error(f"New State: {estado}")
                _logger.error(f"New State: {estado}")
                stack_trace = traceback.format_stack()
                for frame in stack_trace:
                    _logger.error(frame)
        res = super(ExpenseSheet, self).write(vals)
        return res

    def _check_can_create_move(self):
        if any(sheet.state != 'approve' for sheet in self):
            stack_trace = traceback.format_stack()
            _logger.error(f"Stack Trace:")
            for frame in stack_trace:
                _logger.error(frame)
            raise UserError(_("Expense %s state %s is not approve") % (self.name, self.state))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Specify expense journal to generate accounting entries."))

        missing_email_employees = self.filtered(lambda sheet: not sheet.employee_id.work_email).employee_id
        if missing_email_employees:
            action = self.env['ir.actions.actions']._for_xml_id('hr.open_view_employee_tree')
            action['domain'] = [('id', 'in', missing_email_employees.ids)]
            raise RedirectWarning(_("The work email of some employees is missing. Please add it on the employee form"), action, _("Show missing work email employees"))

    def action_sheet_move_create(self):
        """Perform extra checks and set proper payment state according linked
        invoices.
        """
        for expense_line in self.expense_line_ids:
            invoice = expense_line.invoice_id
            if not invoice and not expense_line.advance:
                raise UserError(_("El Gasto %s no tiene una factura asociada") % (expense_line.name))
            for line in invoice.invoice_line_ids:
                line.account_id = expense_line.account_id
            if invoice.state == "draft":
                invoice._post()
        return super().action_sheet_move_create()
