from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'


    def _default_partner_id(self):
        team_id = self.env['helpdesk.team'].search([('member_ids', 'in', self.env.uid)], limit=1).id
        if not team_id:
            team_id = self.env['helpdesk.team'].search([], limit=1).id
        return team_id

    partner_id = fields.Many2one(default=lambda self: self.env.user.partner_id)
        
    user_id = fields.Many2one(
        default=lambda self: self.env.user
    )

    store_collect_date = fields.Datetime("Recolectado en Tienda")
    shop_delivery_date = fields.Datetime("Entregado en Taller")
    shop_return_date = fields.Datetime("Salida de Taller")
    nc_date = fields.Datetime("Solución Administratica o NC")
    pdv_not_delivered_date = fields.Datetime("PDV No Entregado o No Recibido")
    store_delivered_date = fields.Datetime("Entregado en Tienda")

    def write(self, vals):
        # we set the assignation date (assign_date) to now for tickets that are being assigned for the first time
        # same thing for the closing date

        new_stage = vals.get('stage_id')
        if new_stage:
            if new_stage == 2: #Recolectado en tienda
                if not self.store_collect_date:
                    vals['store_collect_date'] = fields.Datetime.now()
            elif new_stage == 3: #Entregado en taller
                if not self.shop_delivery_date:
                    vals['shop_delivery_date'] = fields.Datetime.now()
            elif new_stage == 8: #Salida de taller
                if not self.shop_return_date:
                    vals['shop_return_date'] = fields.Datetime.now()
            elif new_stage == 6: #Solucion Administrativa o NC
                if not self.nc_date:
                    vals['nc_date'] = fields.Datetime.now()
            elif new_stage == 5: #PDV No Entregado o No Recibido
                if not self.pdv_not_delivered_date:
                    vals['pdv_not_delivered_date'] = fields.Datetime.now()
            elif new_stage == 4: #Entregado en Tienda
                if not self.store_delivered_date:
                    vals['store_delivered_date'] = fields.Datetime.now()

        return super().write(vals)
