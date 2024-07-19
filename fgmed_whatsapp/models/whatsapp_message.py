from odoo import models, fields

class WhatsApp_Message(models.Model):
    _name = 'whatsapp_message'
    _description = 'WhatsApp Message'

    mensage = fields.Char(string='Message', required=True)
    contact_id = fields.Many2one('whatsapp_contact', string='Contact', required=True)
    mensage_type = fields.Many2one('whatsapp_type_message', string='Type Message', required=True)
    evento_id = fields.Many2one('whatsapp_event', string='Event')
    send_date = fields.Datetime(string='Send Date')
