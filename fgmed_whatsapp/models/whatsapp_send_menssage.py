from odoo import models, fields, api

class WhatsappSendMessageWizard(models.TransientModel):
    _name = 'whatsapp.send.message.wizard'
    _description = 'WhatsApp Send Message Wizard'

    tag_ids = fields.Many2many('whatsapp_tag', string='Tags')
    contact_ids = fields.Many2many('whatsapp_contact', string='Contacts', compute='_compute_contacts')
    template_id = fields.Many2one('whatsapp_message_layout', string='Message Template', required=True)
    message_content = fields.Text(string='Message Content', compute='_compute_message_content')
    message_type_id = fields.Many2one('whatsapp_type_message', string='Message Type', readonly=True, default=lambda self: self.env['whatsapp_type_message'].create_bot_type().id)

    @api.depends('template_id')
    def _compute_message_content(self):
        for wizard in self:
            wizard.message_content = wizard.template_id.content

    @api.depends('tag_ids')
    def _compute_contacts(self):
        for wizard in self:
            if wizard.tag_ids:
                wizard.contact_ids = self.env['whatsapp_contact'].search([('tag_ids', 'in', wizard.tag_ids.ids)])
            else:
                wizard.contact_ids = False

    def send_messages(self):
        for contact in self.contact_ids:
            self.env['whatsapp_message'].create({
                'mensage': self.message_content,
                'contact_id': contact.id,
                'mensage_type': self.message_type_id.id,
                'send_date': fields.Datetime.now(),
            })
