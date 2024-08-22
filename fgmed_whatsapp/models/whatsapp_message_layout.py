from odoo import models, fields, api

class WhatsappMessageLayout(models.Model):
    _name = 'whatsapp_message_layout'
    _description = 'WhatsApp Message Layout'

    name = fields.Char(string='Name', required=True)
    content = fields.Text(string='Content')
    active = fields.Boolean(string='Active', default=True)
    
    def write(self, vals):
        # Verificar se o campo 'active' está sendo alterado para False
        if 'active' in vals and not vals.get('active', True):
            for record in self:
                # Registrar no histórico de desativação
                self.env['whatsapp_deactivation_history'].create({
                    'model_name': 'whatsapp_message_layout',
                    'record_name': record.name,
                    'deactivated_by': self.env.user.id,
                    'deactivation_date': fields.Datetime.now(),
                })
        return super(WhatsappMessageLayout, self).write(vals)

    def add_newline(self):
        self.content = (self.content or '') + ' | '
    
    def add_contact_name(self):
        self.content = (self.content or '') + ' {contact_name} '

    def add_text(self):
        self.content = (self.content or '') + ' Olá, seu pedido foi enviado. Agradecemos pela sua compra! '

    def add_image(self):
        self.content = (self.content or '') + ' {image_link}|{image_caption} '

    def add_video(self):
        self.content = (self.content or '') + ' {video_link}|{video_caption} '

    def add_audio(self):
        self.content = (self.content or '') + ' {audio_link} '

    def add_document(self):
        self.content = (self.content or '') + ' {document_link}|{document_caption} '

    def add_buttons(self):
        self.content = (self.content or '') + ' {button_text}|{button_reply_1}|{button_reply_2} '

    def add_quick_replies(self):
        self.content = (self.content or '') + ' {quick_reply_header}|{quick_reply_body}|{quick_reply_footer}|{quick_reply_options} '

    def add_full_message(self):
        self.content = (self.content or '') + ' {header_text}|{body_text}|{footer_text}|{button_1}|{button_2} '
