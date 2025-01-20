# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    expense_excess_account_id = fields.Many2one(
        comodel_name='account.account',
        company_dependent=True,
        string="Cuenta Excedentes Gastos",
        help="Cuenta para cargar los excedentes sobre facturas de gastos"
    )

    @api.model_create_multi
    def create(self, vals_list):
        companies = super(ResCompany, self).create(vals_list)
        for company in companies:
            self.env['ir.sequence'].sudo().create({
                'name': 'Secuencia de Activo para %s' % company.name,
                'code': 'asset.sequence',
                'prefix': 'ACT-',
                'padding': 6,
                'company_id': company.id,
            })
        return companies