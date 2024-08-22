from odoo import models, fields, api
from odoo.exceptions import UserError

class WhatsappDuplicateContactWizard(models.TransientModel):
    _name = 'whatsapp.duplicate.contact.wizard'
    _description = 'WhatsApp Duplicate Contact Wizard'

    contact_choices = fields.One2many('whatsapp.duplicate.contact.choice', 'wizard_id', string='Contact Choices')

    def action_confirm(self):
        selected_contacts = self.env['res.partner']
        for choice in self.contact_choices:
            if len(choice.contact_ids) == 0:
                raise UserError(f'Please keep at least one contact for the phone number: {choice.phone_number}')
            if len(choice.contact_ids) == 1:
                choice.selected_contact_id = choice.contact_ids[0]  # Define o único contato como selecionado automaticamente

            selected_contacts |= choice.selected_contact_id

        # Atualiza o wizard original com os contatos selecionados
        send_message_wizard = self.env['whatsapp.send.message.wizard'].browse(self.env.context.get('active_id'))
        send_message_wizard.write({
            'contact_ids': [(6, 0, selected_contacts.ids)]
        })

        # Continua o processo de envio após a confirmação
        send_message_wizard._send_messages_to_contacts()

        # Fecha o wizard
        return {'type': 'ir.actions.act_window_close'}
