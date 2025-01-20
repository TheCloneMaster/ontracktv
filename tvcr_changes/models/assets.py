from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.tools import float_compare, float_is_zero, formatLang, end_of

import logging
_logger = logging.getLogger(__name__)

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset'

    number = fields.Char(string="Número", required=False, copy=False, default='/')
    employee_id = fields.Many2one('hr.employee', 'Asignado a', track_visibility='onchange')
    manufacturer = fields.Char('Marca', size=64)
    model = fields.Char('Modelo', size=64)
    serial = fields.Char('Serie', size=64)
    plate = fields.Char('Placa', size=64)
    chassis = fields.Char('Chasís', size=64)
    cadastral_plan = fields.Char('Plano Catastral.', size=64)

    # stock_location = fields.Many2one(
    #     'stock.location', "Asset Location",
    #     domain=[('usage', 'like', 'asset')],
    #     help="This location will be used as the destination location for installed parts during asset life.")
    # Ubicacion	

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            else:
                self = self.with_company(self.env.company)
            if 'number' not in vals or vals['number'] == '/':
                seq = self.env['ir.sequence'].search([('code', '=', 'asset.sequence'), ('company_id', '=', self.env.company.id)], limit=1)
                if seq:
                    vals['number'] = seq.next_by_id()
                else:
                    vals['number'] = self.env['ir.sequence'].sudo().create({
                        'name': 'Secuencia de Activo para %s' % self.env.company.name,
                        'code': 'asset.sequence',
                        'prefix': 'ACT-',
                        'padding': 5,
                        'company_id': self.env.company.id,
                    }).next_by_id()
        return super().create(vals_list)
    ###########################################
    ###########################################
    ###########################################


    def _recompute_board(self, start_depreciation_date=False):
        self.ensure_one()
        # All depreciation moves that are posted
        posted_depreciation_move_ids = self.depreciation_move_ids.filtered(
            lambda mv: mv.state == 'posted' and not mv.asset_value_change
        ).sorted(key=lambda mv: (mv.date, mv.id))

        imported_amount = self.already_depreciated_amount_import
        residual_amount = self.value_residual
        if not posted_depreciation_move_ids:
            residual_amount += imported_amount
        residual_declining = residual_amount
        # start_yearly_period is needed in the 'degressive' and 'degressive_then_linear' methods to compute the amount when the period is monthly
        start_depreciation_date = start_yearly_period = start_depreciation_date or self.paused_prorata_date
        start_depreciation_date = date(start_depreciation_date.year, start_depreciation_date.month, 1) + relativedelta(months=1) #primer día del mes siguiente
        current_date = fields.Date.context_today(self)
        current_date = date(current_date.year, current_date.month, 1) + relativedelta(months=1) - relativedelta(days=1) #último día del mes actual
        start_depreciation_date = max(start_depreciation_date, current_date)

        #mab last_day_asset = self._get_last_day_asset()
        last_day_asset = date(start_depreciation_date.year, start_depreciation_date.month, 1) + relativedelta(months=self.method_number) - relativedelta(days=1) #último día del último mes a depreciar
        #final_depreciation_date = self._get_end_period_date(last_day_asset)
        final_depreciation_date = last_day_asset
        depreciation_move_values = []
        book_value = self.book_value # - self.value_residual

        if not float_is_zero(book_value, precision_rounding=self.currency_id.rounding) and\
           not float_is_zero(self.method_number, precision_rounding=self.currency_id.rounding):
            depreciation_amount = round(min(self.original_value / self.method_number, book_value),2)

            _logger.info('Name: %s', self.name)
            _logger.info('Book value: %s', self.book_value)
            _logger.info('Book value: %s', self.value_residual)
            _logger.info('Book value: %s', book_value)
            _logger.info('monthly depreciation: %s', depreciation_amount)
            _logger.info('Entrando IF')
            while book_value > 0: # and start_depreciation_date < final_depreciation_date:
                _logger.info('Entrando WHILE')
                period_end_depreciation_date = self._get_end_period_date(start_depreciation_date)
                # period_end_fiscalyear_date = self.company_id.compute_fiscalyear_dates(period_end_depreciation_date).get('date_to')
                # lifetime_left = self._get_delta_days(start_depreciation_date, last_day_asset)
                # days, amount = self._compute_board_amount(residual_amount, start_depreciation_date, period_end_depreciation_date, False, lifetime_left, residual_declining, start_yearly_period)
                amount = min(depreciation_amount, book_value)
                book_value -= amount

                """
                if not posted_depreciation_move_ids:
                    # self.already_depreciated_amount_import management.
                    # Subtracts the imported amount from the first depreciation moves until we reach it
                    # (might skip several depreciation entries)
                    if abs(imported_amount) <= abs(amount):
                        amount -= imported_amount
                        imported_amount = 0
                    else:
                        imported_amount -= amount
                        amount = 0

                if self.method == 'degressive_then_linear' and final_depreciation_date < period_end_depreciation_date:
                    period_end_depreciation_date = final_depreciation_date
                """

                if not float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    # For deferred revenues, we should invert the amounts.
                    depreciation_move_values.append(self.env['account.move']._prepare_move_for_asset_depreciation({
                        'amount': amount,
                        'asset_id': self,
                        'depreciation_beginning_date': start_depreciation_date,
                        'date': period_end_depreciation_date,
                        'asset_number_days': 30, #days,
                    }))

                # if period_end_depreciation_date == period_end_fiscalyear_date:
                #     start_yearly_period = self.company_id.compute_fiscalyear_dates(period_end_depreciation_date).get('date_from') + relativedelta(years=1)
                #     residual_declining = residual_amount

                start_depreciation_date = period_end_depreciation_date + relativedelta(days=1)

        return depreciation_move_values
