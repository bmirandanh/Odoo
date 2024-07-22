from odoo import models, fields, api

class WhatsappEventType(models.Model):
    _name = 'whatsapp_event_type'
    _description = 'WhatsApp Event Type'

    name = fields.Char(string='Type', required=True)
    description = fields.Char(string='Description', required=True)

    @api.model
    def init(self):
        event_types = [
            {'name': 'messages', 'description': 'Evento genérico para mensagens recebidas'},
            {'name': 'messages.message_delivered', 'description': 'Quando uma mensagem é entregue ao destinatário'},
            {'name': 'messages.message_read', 'description': 'Quando uma mensagem é lida pelo destinatário'},
            {'name': 'messages.message_sent', 'description': 'Quando uma mensagem é enviada pelo remetente'},
            {'name': 'group.participant_added', 'description': 'Quando alguém entra em um grupo'},
            {'name': 'group.participant_removed', 'description': 'Quando alguém sai de um grupo'},
            {'name': 'group.subject_changed', 'description': 'Quando o nome do grupo é alterado'},
            {'name': 'group.picture_changed', 'description': 'Quando a imagem do grupo é alterada'},
            {'name': 'group.admin_added', 'description': 'Quando um administrador é adicionado'},
            {'name': 'group.admin_removed', 'description': 'Quando um administrador é removido'},
            {'name': 'messages.image', 'description': 'Envio de fotos'},
            {'name': 'messages.video', 'description': 'Envio de vídeos'},
            {'name': 'messages.document', 'description': 'Envio de documentos'},
            {'name': 'messages.location', 'description': 'Envio de localização'},
            {'name': 'messages.contact', 'description': 'Envio de contatos'},
            {'name': 'messages.audio', 'description': 'Envio de mensagens de áudio'},
            {'name': 'messages.audio_played', 'description': 'Reprodução de mensagens de áudio'},
            {'name': 'calls.voice', 'description': 'Chamadas de voz'},
            {'name': 'calls.video', 'description': 'Chamadas de vídeo'},
            {'name': 'status.update', 'description': 'Atualização de status de usuário'},
            {'name': 'status.read', 'description': 'Visualização do status de outros usuários'},
            {'name': 'reactions', 'description': 'Reações às mensagens'},
            {'name': 'messages.deleted', 'description': 'Mensagem deletada pelo remetente (para si mesmo)'},
            {'name': 'messages.deleted_for_all', 'description': 'Mensagem deletada pelo remetente (para todos)'},
            {'name': 'settings.privacy', 'description': 'Alteração nas configurações de privacidade'},
            {'name': 'settings.notification', 'description': 'Alteração nas configurações de notificação'},
            {'name': 'settings.account', 'description': 'Alteração nas configurações de conta'},
            {'name': 'backup.create', 'description': 'Backup de mensagens'},
            {'name': 'backup.restore', 'description': 'Restauração de mensagens a partir de um backup'},
            {'name': 'messages.automated_response', 'description': 'Mensagens automáticas de chatbot'},
            {'name': 'messages.automated_reply', 'description': 'Respostas automáticas de chatbot'}
        ]

        for event_type in event_types:
            if not self.env['whatsapp_event_type'].search([('name', '=', event_type['name'])]):
                self.env['whatsapp_event_type'].create(event_type)
