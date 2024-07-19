from odoo import models, fields, api

class WhatsAppTypeMessage(models.Model):
    _name = 'whatsapp_type_message'
    _description = 'WhatsApp Type Message'

    name = fields.Char(string='Name', required=True)
    type = fields.Char(string='Type', required=True)

    @api.model
    def create_bot_type(self):
        bot_type = self.search([('type', '=', 'BOT')], limit=1)
        if not bot_type:
            bot_type = self.create({
                'name': 'Bot Message',
                'type': 'BOT'
            })
        return bot_type
