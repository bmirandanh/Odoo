from odoo import models, fields

class whatsapp_event_type(models.Model):
    _name = 'whatsapp_event_type'
    _description = 'WhatsApp Event Type'

    name = fields.Char(string='Type', required=True)
    contact_id = fields.Many2one('whatsapp_contact', string='Contact')
    send_date = fields.Datetime(string='Send Date')