from odoo import fields, models, _

class InformaCliente(models.Model):
    """
    Esta classe representa o cliente do sistema.
    """
    _name = 'informa.cliente'
    _description = 'Cliente do sistema'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    
    name = fields.Char(string='Nome', required=True, tracking=True)
    token = fields.Char(string='Token', required=True, tracking=True)
