from odoo import api, fields, models, _

class APISaleOrderInfo(models.TransientModel):
    _name = 'api.sale.order.info'
    _description = 'API for Sale Order Info'
    
    @api.model
    def get_sale_order_info(self, sale_order_id):
        # Busca o pedido de venda pelo ID fornecido
        sale_order = self.env['sale.order'].browse(sale_order_id)
        
        # Se não encontrar o pedido de venda, retorna erro
        if not sale_order.exists():
            return {"error": _("Sale Order not found!")}
        
        # Atribui o parceiro (cliente) do pedido à variável 'partner'
        partner = sale_order.partner_id
        
        # Atribui as linhas do pedido à variável 'lines'
        lines = sale_order.order_line

        # Trate outros possíveis erros aqui se necessário.

        # Constrói e retorna o dicionário com as informações desejadas
        res = {
            # Informações do pedido de venda
            "sale_order": {
                'id': sale_order.id,
                'partner_id': sale_order.partner_id.id,
                'payment_term_id': sale_order.payment_term_id.id,
                'validity_date': sale_order.validity_date,
                'name': sale_order.name,
                'amount_total': sale_order.amount_total,
                'access_token': sale_order.access_token
            },
            # Informações do parceiro (cliente)
            "partner": {
                'state_id': partner.state_id.id,
                'street': partner.street,
                'l10n_br_number': partner.l10n_br_number,
                'l10n_br_district': partner.l10n_br_district,
                'street2': partner.street2,
                'zip': partner.zip,
                'city': partner.city,
                'mobile': partner.mobile,
                'l10n_br_cnpj_cpf': partner.l10n_br_cnpj_cpf,
                'email': partner.email,
                'name': partner.name,
                'is_company': partner.is_company,
                'phone': partner.phone,
                'city_id': partner.city_id.id
            },
            # Informações das linhas do pedido de venda
            "lines": [{
                'name': line.name,
                'product_id': line.product_id.id,
                'display_name': line.display_name,
                'id': line.id,
                'product_uom_qty': line.product_uom_qty,
                'price_unit': line.price_unit
            } for line in lines],
            # Informações do estado do parceiro (cliente)
            "state": {
                'state_name': partner.state_id.name if partner.state_id else False
            }
        }

        return res
