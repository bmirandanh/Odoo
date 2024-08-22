from odoo import models, fields, api
from odoo.exceptions import UserError
import re
import requests

class WhatsappSendMessageWizard(models.TransientModel):
    _name = 'whatsapp.send.message.wizard'
    _description = 'WhatsApp Send Message Wizard'

    tag_id = fields.Many2one('whatsapp_tag', string='Tag', required=True)
    tag_color = fields.Integer(related='tag_id.tag_color', string='Tag Color', readonly=True)
    contact_ids = fields.Many2many('res.partner', readonly=True, string='Contacts', required=True)
    template_id = fields.Many2one('whatsapp_message_layout', string='Message Template', required=True)
    message_type_id = fields.Many2one('whatsapp_type_message', string='Message Type', readonly=True, default=lambda self: self.env['whatsapp_type_message'].create_bot_type().id)
    campaign_name = fields.Char(string='Campaign Name', required=True)

    @api.model
    def default_get(self, fields):
        res = super(WhatsappSendMessageWizard, self).default_get(fields)
        active_ids = self.env.context.get('default_contact_ids')
        if active_ids:
            leads = self.env['crm.lead'].browse(active_ids)
            partner_ids = leads.mapped('partner_id').filtered(lambda p: p.active)
            res.update({'contact_ids': partner_ids.ids})
        return res

    def send_messages(self):
        if not self.template_id.active:
            raise UserError(f"The selected template '{self.template_id.name}' is inactive and cannot be used.")
        if not self.template_id:
            raise UserError("Please select a message template.")

        # Identificar números de telefone duplicados
        duplicated_contacts = {}
        for contact in self.contact_ids:
            phone_number = contact.mobile or contact.phone
            if phone_number:
                cleaned_phone = self.clean_phone_number(phone_number)
                if cleaned_phone in duplicated_contacts:
                    duplicated_contacts[cleaned_phone].append(contact)
                else:
                    duplicated_contacts[cleaned_phone] = [contact]

        # Se houver contatos duplicados, abrir o wizard para resolução
        choices = []
        for phone_number, contacts in duplicated_contacts.items():
            if len(contacts) > 1:
                choices.append((0, 0, {
                    'phone_number': phone_number,
                    'contact_ids': [(6, 0, [c.id for c in contacts])]
                }))

        if choices:
            # Abrir o wizard para resolver os duplicados
            wizard = self.env['whatsapp.duplicate.contact.wizard'].create({
                'contact_choices': choices
            })
            return {
                'name': 'Resolve Duplicated Contacts',
                'type': 'ir.actions.act_window',
                'res_model': 'whatsapp.duplicate.contact.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        
        # Se não houver duplicados, continue com o envio das mensagens
        self._send_messages_to_contacts()

    def _send_messages_to_contacts(self):
        token = "EAAS74FYKa3ABO9BNfOtPlZCA9ITVmRbj7GZAZAA7IztxQLwZAepI5YcxIJxm0idlKJ3jrzZB74hnrNIadK0YFhjI2wR2LzdvpPdZAbaEtiZChcDRXfZC8jZCDSyaJHdlZCMhnZAZCcEN45JteGGxasg8Rg0skVfdHjJQ1C5ZC2t6D4pYdehDReZAkFXaxxWHfe7mM9tApr"
        conta = "235907209613582"

        for contact in self.contact_ids:
            phone_number = contact.mobile or contact.phone
            cleaned_phone = self.clean_phone_number(phone_number)
            
            parameters = self.extract_parameters_from_content(self.template_id.content, contact)
            self.validate_data(token, conta, self.template_id.name, parameters)

            evento = self.env['whatsapp_event'].create({
                'contact_id': contact.id,
                'type_id': self.env['whatsapp_event_type'].search([('name', '=', 'messages.message_sent')], limit=1).id,
                'send_date': fields.Datetime.now(),
                'status': 'sent'
            })

            message = self.env['whatsapp_message'].create({
                'mensage': self.template_id.content,
                'contact_id': contact.id,
                'mensage_type': self.message_type_id.id,
                'evento_id': evento.id,
                'send_date': fields.Datetime.now(),
                'campaign_name': self.campaign_name,
                'sent_by': self.env.user.id,
                'contacts_sent': [(6, 0, self.contact_ids.ids)],
                'tag_ids': [(6, 0, self.tag_id.ids)],
            })

            evento.write({'message_id': message.id})

            payload = {
                "messaging_product": "whatsapp",
                "to": cleaned_phone,
                "type": "template",
                "template": {
                    "name": self.template_id.name,
                    "language": {"code": "pt_BR"},
                    "components": [{"type": "body", "parameters": parameters}]
                }
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            try:
                response = requests.post(f"https://graph.facebook.com/v20.0/{conta}/messages", headers=headers, json=payload)
                if response.status_code != 200:
                    raise UserError(f"Failed to send message to {cleaned_phone}: {response.json()}")
            except requests.exceptions.RequestException as e:
                raise UserError(f"An error occurred while sending the message: {str(e)}")

    def clean_phone_number(self, phone_number):
        return re.sub(r'[^\d+]', '', phone_number)

    def extract_parameters_from_content(self, content, contact):
        if not content:
            raise UserError("Template content is empty.")
        content = content.replace('{contact_name}', contact.name)
        parts = [part.strip() for part in content.split('|') if part.strip()]
        if len(parts) == 0:
            raise UserError("No valid parameters found in the template content.")
        return [{"type": "text", "text": part} for part in parts]

    def validate_data(self, token, conta, template_name, parameters):
        if not token or len(token) < 20:
            raise UserError("Invalid or missing token. Please check your API token.")
        if not conta:
            raise UserError("Invalid or missing WhatsApp account ID (WA_ACCOUNT1).")
        if not template_name:
            raise UserError("Template name cannot be empty.")
        if not parameters:
            raise UserError("Template parameters cannot be empty.")
