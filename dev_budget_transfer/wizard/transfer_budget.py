# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################


from odoo import models, fields, _
from odoo.exceptions import ValidationError


class transfer_budget(models.TransientModel):
    _name = 'transfer.budget'
    _description = 'Budget Transfer'

    def transfer_budget(self):
        if self.amount > self.from_budget_line_id.planned_amount:
            raise ValidationError(
                _('''You can not transfer more than your balance, balance is %s ! ''') % (self.from_budget_line_id.planned_amount))

        self.to_budget_line_id.planned_amount += self.amount
        self.from_budget_line_id.planned_amount -= self.amount
        vals = {
            'from_budget_id': self.from_budget_id and self.from_budget_id.id or False,
            'to_budget_id': self.to_budget_id and self.to_budget_id.id or False,
            'from_budget_line_id': self.from_budget_line_id and self.from_budget_line_id.id or False,
            'to_budget_line_id': self.to_budget_line_id and self.to_budget_line_id.id or False,
            'date': self.date or False,
            'notes': self.notes or '',
            'amount': self.amount,
            'company_id': self.company_id and self.company_id.id or False,
        }
        self.env['transfer.budget.history'].sudo().create(vals)

    from_budget_id = fields.Many2one('crossovered.budget', string="From Budget", required=True)
    to_budget_id = fields.Many2one('crossovered.budget', string="To Budget", required=True)
    date = fields.Date(string="Date", default=fields.Date.today())
    notes = fields.Text(string="Notes")
    from_budget_line_id = fields.Many2one('crossovered.budget.lines', string="From Budget Line", required=True)
    to_budget_line_id = fields.Many2one('crossovered.budget.lines', string="To Budget Line", required=True)
    amount = fields.Monetary(string="Amount", required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
