from odoo import models, fields

class whatsapp_type_message(models.Model):
    _name = 'whatsapp_type_message'
    _description = 'WhatsApp type Message'

    name = fields.Char(string='Message', required=True)
    type = fields.Char(string='type', required=True)

