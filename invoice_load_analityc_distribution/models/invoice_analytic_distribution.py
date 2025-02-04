from odoo import models, fields, api
import xlrd
import base64
import json

class InvoiceAnalyticDistributionWizard(models.TransientModel):
    _name = 'invoice.analytic.distribution.wizard'
    _description = 'Asistente para carga de distribución analítica'

    excel_file = fields.Binary(string='Archivo Excel', required=True, attachment=True)
    filename = fields.Char(string='Nombre del archivo')
    tipo = fields.Selection(
        selection=[('porcentaje', 'Porcentaje'), ('monto', 'Monto')],
        string='Tipo de Distribución',
        required=True,
        default='porcentaje'
    )
    

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
        total = 0
        for row in range(1, sheet.nrows):
            code = sheet.cell_value(row, 0).rstrip('-')
            value = sheet.cell_value(row, 1)
            if not value:
                continue
            
            analytic_account = self.env['account.analytic.account'].search([('code', '=', code)], limit=1)
            if not analytic_account:
                raise models.ValidationError(f'Cuenta analítica no encontrada: {code}')
            
            distribution[str(analytic_account.id)] = value
            total += value

        if self.tipo == 'porcentaje':
            if abs(total - 1) > 0.0001:
                raise models.ValidationError('La suma de porcentajes debe ser 100%')
            for acc_id in distribution:
                distribution[acc_id] = distribution[acc_id] * 100
        else:
            invoice_total = sum(invoice.invoice_line_ids.mapped('price_subtotal'))
            if abs(total - invoice_total) > 0.01:
                raise models.ValidationError(f'Total de montos ({total}) no coincide con total de factura ({invoice_total})')
            for acc_id in distribution:
                distribution[acc_id] = (distribution[acc_id] / total) * 100
        
        # Aplicar distribución a las líneas
        for line in invoice.invoice_line_ids:
            line.write({
                'analytic_distribution': distribution
            })
        
        return {'type': 'ir.actions.act_window_close'}
