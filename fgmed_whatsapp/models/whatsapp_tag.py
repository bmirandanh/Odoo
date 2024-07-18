from odoo import models, fields

class whatsapp_tag(models.Model):
    _name = 'whatsapp_tag'
    _description = 'WhatsApp Tag'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')
