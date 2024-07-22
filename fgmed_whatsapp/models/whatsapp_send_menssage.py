import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

class WhatsappSendMessageWizard(models.TransientModel):
    _name = 'whatsapp.send.message.wizard'
    _description = 'WhatsApp Send Message Wizard'

    tag_ids = fields.Many2many('whatsapp_tag', string='Tags')
    contact_ids = fields.Many2many('whatsapp_contact', string='Contacts', compute='_compute_contacts')
    template_id = fields.Many2one('whatsapp_message_layout', string='Message Template', required=True)
    message_type_id = fields.Many2one('whatsapp_type_message', string='Message Type', readonly=True, default=lambda self: self.env['whatsapp_type_message'].create_bot_type().id)

    @api.depends('tag_ids')
    def _compute_contacts(self):
        for wizard in self:
            if wizard.tag_ids:
                wizard.contact_ids = self.env['whatsapp_contact'].search([('tag_ids', 'in', wizard.tag_ids.ids)])
            else:
                wizard.contact_ids = False
                
    #def send_whatsapp_message(self, waid, message):
     #    url = "https://api.whatsapp.com/send"  # Substitua pela URL da API de envio do WhatsApp que você está usando
     #    headers = {
     #        "Content-Type": "application/json",
     #        "Authorization": "Bearer YOUR_API_KEY"  # Substitua YOUR_API_KEY pelo token da sua API
     #    }
    #     payload = {
     #        "phone": waid,
     #        "message": message
    #     }
    #     response = requests.post(url, headers=headers, json=payload)
     #    if response.status_code != 200:
    #         raise UserError(f"Failed to send message to {waid}: {response.text}")

    def send_messages(self):
        if not self.template_id:
            raise UserError("Please select a message template.")

        # Obter o ID do tipo de evento 'messages.message_sent'
        event_type = self.env['whatsapp_event_type'].search([('name', '=', 'messages.message_sent')], limit=1)
        if not event_type:
            raise UserError("The event type 'messages.message_sent' was not found.")
        
        for contact in self.contact_ids:
            # Criar evento de WhatsApp com status 'sent' e type_id 'messages.message_sent'
            evento = self.env['whatsapp_event'].create({
                'contact_id': contact.id,
                'type_id': event_type.id,  # Use o ID correto do tipo de evento
                'send_date': fields.Datetime.now(),
                'status': 'sent'
            })

            # Enviar mensagem via API do WhatsApp
            #self.send_whatsapp_message(contact.waid, self.template_id.content)

            # Criar registro de mensagem no Odoo e referenciar o evento criado
            self.env['whatsapp_message'].create({
                'mensage': self.template_id.content,
                'contact_id': contact.id,
                'mensage_type': self.message_type_id.id,
                'evento_id': evento.id,  # Referenciando o evento criado
                'send_date': fields.Datetime.now(),
            })