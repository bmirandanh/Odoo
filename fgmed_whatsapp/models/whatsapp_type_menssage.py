from odoo import models, fields, api

class WhatsAppTypeMessage(models.Model):
    _name = 'whatsapp_type_message'
    _description = 'WhatsApp Type Message'

    name = fields.Char(string='Name', required=True)
    type = fields.Selection([
        ('text', 'Text'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('sticker', 'Sticker'),
        ('location', 'Location'),
        ('contacts', 'Contacts'),
        ('interactive', 'Interactive'),
        ('list', 'List'),
        ('button', 'Button'),
        ('template', 'Template'),
        ('template_text', 'Template Text'),
        ('template_media', 'Template Media'),
        ('button_quick_reply', 'Button Quick Reply'),
        ('button_url', 'Button URL'),
        ('button_call', 'Button Call'),
        ('bot', 'BOT')
    ], string='Type', required=True)

    @api.model
    def create_bot_type(self):
        bot_type = self.search([('type', '=', 'bot')], limit=1)
        if not bot_type:
            bot_type = self.create({
                'name': 'Bot Message',
                'type': 'bot'
            })
        return bot_type

    @api.model
    def create_default_types(self):
        types = [
            {'name': 'Text Message', 'type': 'text'},
            {'name': 'Image Message', 'type': 'image'},
            {'name': 'Audio Message', 'type': 'audio'},
            {'name': 'Video Message', 'type': 'video'},
            {'name': 'Document Message', 'type': 'document'},
            {'name': 'Sticker Message', 'type': 'sticker'},
            {'name': 'Location Message', 'type': 'location'},
            {'name': 'Contacts Message', 'type': 'contacts'},
            {'name': 'Interactive Message', 'type': 'interactive'},
            {'name': 'List Message', 'type': 'list'},
            {'name': 'Button Message', 'type': 'button'},
            {'name': 'Template Message', 'type': 'template'},
            {'name': 'Template Text Message', 'type': 'template_text'},
            {'name': 'Template Media Message', 'type': 'template_media'},
            {'name': 'Button Quick Reply', 'type': 'button_quick_reply'},
            {'name': 'Button URL', 'type': 'button_url'},
            {'name': 'Button Call', 'type': 'button_call'},
            {'name': 'Bot Message', 'type': 'bot'},
        ]
        for type_data in types:
            if not self.search([('type', '=', type_data['type'])], limit=1):
                self.create(type_data)

    @api.model
    def init(self):
        self.create_default_types()
