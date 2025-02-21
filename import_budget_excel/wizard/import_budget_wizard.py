import base64
import xlrd
from odoo import models, fields, api, _
from odoo.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)

class ImportBudgetWizard(models.TransientModel):
    _name = 'import.budget.wizard'
    _description = 'Importar Presupuesto desde Excel'

    excel_file = fields.Binary(string='Archivo Excel', required=True)
    budget_id = fields.Many2one('crossovered.budget', string='Presupuesto', required=True)

    def import_budget(self):
        # Decodificar el archivo Excel
        try:
            file_data = base64.b64decode(self.excel_file)
            workbook = xlrd.open_workbook(file_contents=file_data)
            sheet = workbook.sheet_by_name('Gastos')
        except xlrd.biffh.XLRDError:
            raise UserError(_("El nombre de la hoja debe ser 'Gastos'."))
        except Exception as e:
            raise UserError(_("Error al procesar el archivo Excel: %s") % e)

        # Mapear las columnas de meses a índices
        month_columns = {
            'Enero': 10, 'Febrero': 11, 'Marzo': 12, 'Abril': 13,
            'Mayo': 14, 'Junio': 15, 'Julio': 16, 'Agosto': 17,
            'Septiembre': 18, 'Octubre': 19, 'Noviembre': 20, 'Diciembre': 21
        }

        budget_lines_to_create = []

        # Procesar cada fila de la hoja de Excel
        for row_num in range(1, sheet.nrows):
            row = sheet.row(row_num)
            if row_num % 500 == 0:
                message = "Procesados %s / %s lineas de presupuesto\n" % (row_num, sheet.nrows)
                self.env(context=self.env.user.context_get())['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                    'type': 'info',
                    'message': message,
                    'sticky': False,
                })
                _logger.error("CARGA: Procesados %s / %s lineas de presupuesto\n", row_num, sheet.nrows)

            analytic_account_code = str(row[0].value).strip()
            account_code = str(row[1].value).strip()

            # Buscar la cuenta analítica
            analytic_account = self.env['account.analytic.account'].search([('code', '=', analytic_account_code)], limit=1)
            if not analytic_account:
                message = "Cuenta analítica: %s no homologada de la línea de presupuesto: %s\n" % (analytic_account_code, row_num)
                self.env(context=self.env.user.context_get())['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                    'type': 'danger',
                    'message': message,
                    'sticky': True,
                })
                _logger.error("CARGA: Cuenta analítica: %s no homologada de la línea de presupuesto: %s", analytic_account_code, row_num)
                continue

            # Buscar la cuenta contable
            account = self.env['account.account'].search([('code', '=', account_code)], limit=1)
            if not account:
                message = "Cuenta contable: %s no homologada de la línea de presupuesto: %s\n" % (account_code, row_num)
                self.env(context=self.env.user.context_get())['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                    'type': 'danger',
                    'message': message,
                    'sticky': True,
                })
                _logger.error("CARGA: Cuenta contable: %s no homologada de la línea de presupuesto: %s", account_code, row_num)
                continue

            # Buscar o crear la posición presupuestaria relacionada con la cuenta contable
            budget_position = self.env['account.budget.post'].search([
                ('account_ids', 'in', [account.id]),
                # ('budget_line_ids.crossovered_budget_id', '=', self.budget_id.id)
            ], limit=1)
            if not budget_position:
                budget_position = self.env['account.budget.post'].create({
                    'name': f'{account.code} - {account.name}', # ({self.budget_id.name})',
                    'account_ids': [(4, account.id)],  # Agregar la cuenta a la posición
                    'company_id': self.env.company.id,
                    # 'budget_line_ids': [(0, 0, {'crossovered_budget_id': self.budget_id.id})]
                })

            year = self.budget_id.date_from.year

            # Procesar cada mes
            for month, col_index in month_columns.items():
                try:
                    # amount = abs(row[col_index].value)
                    amount = -row[col_index].value
                except Exception as e:
                    _logger.error("Error al procesar el monto para el mes %s: %s", col_index, row[col_index].value)
                    continue
                if amount:  # Solo procesar si hay un monto asignado
                    # Crear la línea de presupuesto
                    existing_line = self.env['crossovered.budget.lines'].search([
                        ('crossovered_budget_id', '=', self.budget_id.id),
                        ('analytic_account_id', '=', analytic_account.id),
                        ('general_budget_id', '=', budget_position.id),
                        ('date_from', '=', fields.Date.from_string(f'{year}-{str(list(month_columns.keys()).index(month) + 1).zfill(2)}-01')),
                        ('date_to', '=', fields.Date.from_string(f'{year}-{str(list(month_columns.keys()).index(month) + 1).zfill(2)}-28')), # asumiendo febrero
                    ], limit=1)

                    if existing_line:
                        # Si existe, sumar el nuevo monto al monto existente
                        existing_line.write({'planned_amount': existing_line.planned_amount + amount})
                    else:
                        # Si no existe, crear una nueva línea de presupuesto
                        self.env['crossovered.budget.lines'].create({
                            'crossovered_budget_id': self.budget_id.id,
                            'analytic_account_id': analytic_account.id,
                            'general_budget_id': budget_position.id,
                            'date_from': fields.Date.from_string(f'{year}-{str(list(month_columns.keys()).index(month) + 1).zfill(2)}-01'),
                            'date_to': fields.Date.from_string(f'{year}-{str(list(month_columns.keys()).index(month) + 1).zfill(2)}-28'), # asumiendo febrero
                            'planned_amount': amount,
                        })

        # # Crear las líneas de presupuesto en Odoo
        # if budget_lines_to_create:
        #     self.env['crossovered.budget.lines'].create(budget_lines_to_create)

        return {'type': 'ir.actions.act_window_close'}
    
    @api.model
    def default_get(self, fields):
        # Este método se llama cuando se abre el wizard.
        # Se usa para establecer valores por defecto en los campos.

        res = super(ImportBudgetWizard, self).default_get(fields)
        
        # Comprueba si la clave 'active_id' está presente en el contexto.
        # Si es así, establece el valor del campo 'budget_id' del wizard
        # con el valor de 'active_id'. Esto se hace para pre-rellenar
        # el campo 'budget_id' con el ID del presupuesto actual desde
        # donde se llama al wizard.
        if 'active_id' in self.env.context:
            res['budget_id'] = self.env.context['active_id']
        return res