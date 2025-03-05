from odoo import models, fields, api, _, exceptions
#from odoo.addons.web.controllers.utils import get_service
from zeep import Client
from zeep.transports import Transport
from datetime import datetime, timedelta, timezone
import logging

_logger = logging.getLogger(__name__)

class TVCRConexionComercial(models.Model):
    _name = 'tvcr.conexion.comercial'
    _description = 'Conexión Comercial TVCR'

    def _get_wsdl_url(self):
      return "http://ws.teletica.cr/ordenescontinuidad/VerticeServices.asmx?wsdl"

    def _get_service_url(self):
      return "http://ws.teletica.cr/ordenescontinuidad/VerticeServices.asmx"

    def _authenticate(self):
        # Autenticación SOAP
        transport = Transport(timeout=120)
        client = Client(wsdl=self._get_wsdl_url(), transport=transport)
        try:
            response = client.service.Autentificacion(usuario='admin', contrasenna='admin')
            if response.Autenticado:
                self.env['ir.config_parameter'].sudo().set_param('tvcr.token', response.Token)
                self.env['ir.config_parameter'].sudo().set_param('tvcr.vigencia', response.Vigencia.isoformat())
                _logger.info("Autenticación exitosa con TVCR. Token: %s, Vigencia: %s", response.Token, response.Vigencia)
            else:
                _logger.error("Error en la autenticación con TVCR.")
                raise exceptions.UserError(_("Error en la autenticación con TVCR."))
        except Exception as e:
            _logger.error("Error al autenticar con TVCR: %s", e)
            raise exceptions.UserError(_("Error al autenticar con TVCR: %s") % e)

    def _check_valid_token(self):
        # Verificar vigencia del token
        vigencia_str = self.env['ir.config_parameter'].sudo().get_param('tvcr.vigencia')
        if vigencia_str:
            vigencia = datetime.fromisoformat(vigencia_str)
            # Convertir vigencia a UTC si ya tiene zona horaria
            if vigencia.tzinfo:
                vigencia = vigencia.astimezone(timezone.utc).replace(tzinfo=None)

            # Obtener la hora actual en UTC
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

            if vigencia < now_utc:
                self._authenticate()
        else:
            self._authenticate()

    def _get_pending_orders(self):
        # Obtener órdenes pendientes
        self._check_valid_token()
        token = self.env['ir.config_parameter'].sudo().get_param('tvcr.token')
        transport = Transport(timeout=120)
        client = Client(wsdl=self._get_wsdl_url(), transport=transport)
        try:
            response = client.service.ObtenerOrdenesPendientes(token=token, organizacionId=10)
            #_logger.info("Órdenes pendientes de TVCR: %s", response)
            return response #.ObtenerOrdenesPendientesResult.OrdenCompraFacturacion if hasattr(response, 'ObtenerOrdenesPendientesResult') and hasattr(response.ObtenerOrdenesPendientesResult, 'OrdenCompraFacturacion') else []
        except Exception as e:
            _logger.error("Error al obtener órdenes pendientes de TVCR: %s", e)
            raise exceptions.UserError(_("Error al obtener órdenes pendientes de TVCR: %s") % e)

    def _get_order_lines(self, order_id):
        # Obtener líneas de una orden específica
        self._check_valid_token()
        token = self.env['ir.config_parameter'].sudo().get_param('tvcr.token')
        transport = Transport(timeout=120)
        client = Client(wsdl=self._get_wsdl_url(), transport=transport)
        try:
            response = client.service.ObtenerOrdenCompraLineasPorOrden(token=token, organizacionId=10, ordenCompraId=order_id)
            return response #.ObtenerOrdenCompraLineasPorOrdenResult.LineasOrdenesCompra if hasattr(response, 'ObtenerOrdenCompraLineasPorOrdenResult') and hasattr(response.ObtenerOrdenCompraLineasPorOrdenResult, 'LineasOrdenesCompra') else []
        except Exception as e:
            _logger.error("Error al obtener líneas de la orden %s de TVCR: %s", order_id, e)
            raise exceptions.UserError(_("Error al obtener líneas de la orden %s de TVCR: %s") % (order_id, e))

    def _map_order_data(self, order_data):
        # Mapear datos de la orden a campos de Odoo
        partner = self.env['res.partner'].search([('vat', '=', order_data.IdentificacionCliente), ('ref', 'like', 'CLI-')], limit=1)
        if not partner:
            _logger.error("Datos de orden: %s", order_data)
            message = "Cliente: %s no homologado de la Orden Comercial: %s\n" % (order_data.IdentificacionCliente,order_data.OrdenCompraId)
            self.env(context=self.env.user.context_get())['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                'type': 'danger',
                'message': message,
                'sticky': True,
            })
            raise exceptions.UserError(message)
        partner_shipping_id = self.env['res.partner'].search([('vat', '=', order_data.IdentificacionAgencia)], limit=1)
        currency_name = order_data.MonedaID = 'C' and 'CRC' or 'USD'
        currency_id = self.env['res.currency'].search([('name', '=', currency_name)], limit=1)

        return {
            'partner_id': partner.id,
            'partner_shipping_id': partner_shipping_id.id,
            'date_order': order_data.FechaOrden,
            'note': order_data.Observaciones,
            'client_order_ref': order_data.NumeroOrdenCliente,
            'origin': order_data.OrdenCompraId,
            'company_id': self.env.company.id,
            'currency_id': currency_id.id,
            'user_id': self.env.user.id,
            'order_line': [],
            # 'external_order_id': order_data.OrdenCompraId, #Campo nuevo para ID externo
        }

    def _map_order_line_data(self, comercial_order, order_line_data):
        # Mapear datos de la línea de orden a campos de Odoo
        product = self.env['product.product'].search([('default_code', '=', order_line_data.ProgramaTransmisionId)], limit=1)
        if not product: 
            message = "Producto: %s no homologado de la Orden Comercial: %s\n" % (order_line_data.ProgramaTransmisionId,comercial_order)
            self.env(context=self.env.user.context_get())['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                'type': 'danger',
                'message': message,
                'sticky': True,
            })
            raise exceptions.UserError(message)
            # product = self.env['product.product'].search([('default_code', '=', 'XXcomercialxx')], limit=1)
        # if not product:
        #     product = self.env['product.product'].create({
        #         # 'name': order_line_data.NombrePrograma,
        #         'name': 'Producto importado de Comercial',
        #         # 'default_code': order_line_data.CodigoProducto,
        #         'default_code': 'XXcomercialxx',
        #         'type': 'service',
        #         'invoice_policy': 'order',
        #     })
        iva_tax = periodistas_tax= []
        if order_line_data.ImpuestoVenta:
            iva_tax = self.get_taxes(order_line_data.ImpuestoVenta)
        if order_line_data.ImpuestoPeriodistas:
            periodistas_tax = self.get_taxes(order_line_data.ImpuestoPeriodistas)
        taxes = [tax.id for tax in product.taxes_id]
        return {
            'product_id': product and product.id,
            'product_uom_qty': 1, #order_line_data.Cantidad,
            'price_unit': order_line_data.Precio,
            'discount_conf_id': self.env.ref(
                        'invoice_discount_per_line.advance_discount_selection_percentage').id,
            # 'discount': order_line_data.PorcentajeDescuento,
            'advance_discount': order_line_data.MontoDescuento,
            'name': order_line_data.ProductoCliente,
            # 'name': str(order_line_data.Cantidad) + ' ' + order_line_data.NombrePrograma + ' - ' + order_line_data.ProductoCliente,
            # 'tax_id': [(6, 0, iva_tax+periodistas_tax)], #Funcion para obtener impuestos
            'tax_id': [(6, 0, taxes)], 
        }

    def get_taxes(self, tax_amount):
      # Función para obtener impuestos
      if tax_amount > 0:
        tax = self.env['account.tax'].search([('amount','=',tax_amount)], limit=1)
        # if not tax:
        #   tax = self.env['account.tax'].create({
        #       'name': 'Impuesto de Venta (Calculado desde TVCR)',
        #       'amount_type': 'percent',
        #       'amount': tax_amount,
        #       'type_tax_use': 'sale',
        #       'description': 'IV ' + str(tax_amount) + '%',
        #   })
        return tax and [tax.id] or []
      return []

    def _call_cambiar_estado_ordenes(self, ordenes):
        # Función genérica para llamar a CambiarEstadoOrdenesCompra
        #return True
        self._check_valid_token()
        token = self.env['ir.config_parameter'].sudo().get_param('tvcr.token')
        transport = Transport(timeout=120)
        client = Client(wsdl=self._get_wsdl_url(), transport=transport)
        try:
            response = client.service.CambiarEstadoOrdenesCompra(
                token=token,
                organizacionId=10,
                ordenes=ordenes
            )
            _logger.info("Respuesta de CambiarEstadoOrdenesCompra: %s lista: %s", response,ordenes)
            return response
        except Exception as e:
            _logger.error("Error al llamar a CambiarEstadoOrdenesCompra: %s", e)
            raise exceptions.UserError(_("Error al llamar a CambiarEstadoOrdenesCompra: %s") % e)

    def _create_sale_orders(self):
        # Crear órdenes de venta en Odoo
        orders_data = self._get_pending_orders()
        sale_order_model = self.env['sale.order']
        sale_order_line_model = self.env['sale.order.line']
        created_orders = 0
        ordenes_creadas = []  # Lista para almacenar las órdenes creadas
        total_errors  = ""
        for order_data in orders_data:
            order_errors = ""
            existing_order = sale_order_model.search([('origin', '=', order_data.OrdenCompraId)], limit=1)
            if existing_order:
                _logger.info("La orden con ID externo %s ya existe en Odoo. Se omite su creación.", order_data.OrdenCompraId)
                continue

            if created_orders >= 10:
                continue
            
            try:
                order_vals = self._map_order_data(order_data)
            except Exception as e:
                order_errors += str(e)
                continue
            order_lines = []
            # Obtener líneas de la orden actual
            lines_data = self._get_order_lines(order_data.OrdenCompraId)
            if lines_data:
                for line_data in lines_data:
                    try:
                        line_vals = self._map_order_line_data(order_vals['origin'], line_data)
                    except Exception as e:
                        order_errors += str(e)
                        continue
                    # sale_order_line_model.create(line_vals)
                    order_lines.append((0, 0, line_vals))
                order_vals['order_line'] = order_lines
            if order_errors:
                total_errors += order_errors
            else:
                order = sale_order_model.create(order_vals)
                _logger.info("Orden de venta creada en Odoo: %s", order.name)
                created_orders+=1
                ordenes_creadas.append(order_data.OrdenCompraId) # Agregar ID a la lista
        # Llamar a CambiarEstadoOrdenesCompra para las órdenes creadas
        if ordenes_creadas:
            for order_id in ordenes_creadas:
                ordenes_para_cambiar_estado = [
                    { 'OrdenCompra': {
                        'OrganizationId': 10,
                        'OrdenCompraId': order_id,
                        'EstadoDocumentoNuevoId': 7
                    }}
                ]
                self._call_cambiar_estado_ordenes(ordenes_para_cambiar_estado)

        # if total_errors:
        #     self.env(context=self.env.user.context_get())['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
        #         'type': 'danger',
        #         'message': total_errors,
        #         'sticky': True,
        #     })
        #     # return {
        #     #     'type': 'ir.actions.client',
        #     #     'tag': 'display_notification',
        #     #     'params': {
        #     #         'title': "Error de carga",
        #     #         'message': total_errors,
        #     #         'sticky': True,
        #     #     }
        #     # }

    @api.model
    def load_pending_orders(self):
        # Acción para cargar órdenes pendientes (llamada desde el botón)
        self._create_sale_orders()

    @api.model
    def scheduled_load_pending_orders(self):
        # Acción programada para cargar órdenes pendientes
        _logger.info("Ejecutando acción programada para cargar órdenes pendientes de TVCR.")
        self._create_sale_orders()

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def unlink(self):
        # Llamar a CambiarEstadoOrdenesCompra antes de eliminar la orden
        for order_id in self:
            ordenes_para_cambiar_estado = [
                { 'OrdenCompra': {
                    'OrganizationId': 10,
                    'OrdenCompraId': order_id.origin,
                    'EstadoDocumentoNuevoId': 5
                }}
            ]
            self.env['tvcr.conexion.comercial']._call_cambiar_estado_ordenes(ordenes_para_cambiar_estado)
        return super(SaleOrder, self).unlink()