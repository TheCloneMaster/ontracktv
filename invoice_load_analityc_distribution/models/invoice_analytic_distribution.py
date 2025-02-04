from odoo import models, fields, api
import xlrd
import base64
import json

class InvoiceAnalyticDistributionWizard(models.TransientModel):
    _name = 'invoice.analytic.distribution.wizard'
    _description = 'Asistente para carga de distribución analítica'

    excel_file = fields.Binary(string='Archivo Excel', required=True, attachment=True)
    filename = fields.Char(string='Nombre del archivo')

    def process_file(self):
        self.ensure_one()
        invoice = self.env['account.move'].browse(self._context.get('active_id'))
        
        # Leer archivo Excel
        file_content = base64.decodebytes(self.excel_file)
        book = xlrd.open_workbook(file_contents=file_content)
        sheet = book.sheet_by_index(0)
        
        # Validar estructura
        if sheet.ncols < 2:
            raise models.ValidationError('El archivo debe tener al menos 2 columnas')
        
        # Procesar filas
        distribution = {}
        total_percent = 0
        for row in range(1, sheet.nrows):
            code = sheet.cell_value(row, 0)
            # name = sheet.cell_value(row, 1)
            percent = sheet.cell_value(row, 1)
            if not percent:
                continue
            
            analytic_account = self.env['account.analytic.account'].search([('code', '=', code)], limit=1)
            if not analytic_account:
                raise models.ValidationError(f'Cuenta analítica no encontrada: {code}')
            
            distribution[str(analytic_account.id)] = percent
            total_percent += percent
        
        # Validar suma de porcentajes
        if round(total_percent, 2) != 100:
            raise models.ValidationError('La suma de porcentajes debe ser 100%')

        json_result = json.dumps(distribution)
        # Aplicar distribución a las líneas
        for line in invoice.invoice_line_ids:
            line.write({
                'analytic_distribution': distribution
            })
        
        return {'type': 'ir.actions.act_window_close'}
