from odoo import models, fields

class whatsapp_message_layout(models.Model):
    _name = 'whatsapp_message_layout'
    _description = 'WhatsApp Message Layout'

    name = fields.Char(string='Name', required=True)
    content = fields.Text(string='Content')
    active = fields.Boolean(string='Active', default=True)
