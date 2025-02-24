# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd
#    (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields


class TransferBudgetHistory(models.Model):
    _name = 'transfer.budget.history'
    _description = 'Transfer Budget History'
    _order = "id desc"

    from_budget_id = fields.Many2one('crossovered.budget', string="From Budget")
    to_budget_id = fields.Many2one('crossovered.budget', string="To Budget")
    date = fields.Date(string="Date", default=fields.Date.today())
    notes = fields.Text(string="Notes")
    from_budget_line_id = fields.Many2one('crossovered.budget.lines', string="From Budget Line")
    to_budget_line_id = fields.Many2one('crossovered.budget.lines', string="To Budget Line")
    amount = fields.Monetary(string="Amount")
    company_id = fields.Many2one('res.company', string='Company')
    currency_id = fields.Many2one('res.currency', string='Currency')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: