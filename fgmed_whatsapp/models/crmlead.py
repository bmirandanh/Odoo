from odoo import models, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_send_whatsapp(self):
        # Verifica se algum lead foi selecionado
        if not self:
            return

        # Obter IDs dos contatos associados aos leads selecionados
        partner_ids = self.mapped('partner_id').filtered(lambda p: p.active).ids
        
        # Verifica se há contatos válidos
        if not partner_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No valid contacts',
                    'message': 'No active contacts are associated with the selected leads.',
                    'type': 'danger',
                    'sticky': False,
                }
            }

        # Abrir o wizard de envio de mensagens WhatsApp com os contatos selecionados
        return {
            'name': 'Send WhatsApp Message',
            'type': 'ir.actions.act_window',
            'res_model': 'whatsapp.send.message.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('whatsapp_send_message_view_form').id,  # Referência da view do wizard
            'target': 'new',
            'context': {
                'default_contact_ids': partner_ids,
            },
        }
