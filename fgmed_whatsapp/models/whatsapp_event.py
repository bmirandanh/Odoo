from odoo import models, fields

class whatsapp_event(models.Model):
    _name = 'whatsapp_event'
    _description = 'WhatsApp Event'

    contact_id = fields.Many2one('whatsapp_contact', string='Contact', required=True)
    type_id = fields.Many2one('whatsapp_event_type', string='Event Type', required=True)
    send_date = fields.Datetime(string='Send Date')
    status = fields.Char(string='Status')
