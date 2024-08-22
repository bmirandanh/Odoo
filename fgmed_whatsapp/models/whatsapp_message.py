from odoo import models, fields, api

class WhatsApp_Message(models.Model):
    _name = 'whatsapp_message'
    _description = 'WhatsApp Message'

    mensage = fields.Char(string='Message', required=True)
    contact_id = fields.Many2one('res.partner', string='Contact', required=True)
    mensage_type = fields.Many2one('whatsapp_type_message', string='Type Message', required=True)
    evento_id = fields.Many2one('whatsapp_event', string='Event')
    send_date = fields.Datetime(string='Send Date')
    tag_ids = fields.Many2many('whatsapp_tag', string='Tag')  # Associando diretamente as tags

    # Campo computado para cores das tags
    tag_color = fields.Html(string="Tag Colors", compute="_compute_tag_colors", sanitize=False)

    # Campos adicionais para campanha
    campaign_name = fields.Char(string='Campaign Name')
    sent_by = fields.Many2one('res.users', string='Sent By')
    contacts_sent = fields.Many2many('res.partner', string='Contacts Sent')

    COLOR_MAP = {
        0: "#FFFFFF",  # branco
        1: "#FFC0CB",  # rosa claro
        2: "#FFA07A",  # salmão claro
        3: "#FFD700",  # dourado
        4: "#87CEEB",  # azul claro
        5: "#DDA0DD",  # ameixa
        6: "#FF4500",  # laranja avermelhado
        7: "#1E90FF",  # azul dócil
        8: "#32CD32",  # verde lima
        9: "#8A2BE2",  # azul violeta
        10: "#FF1493",  # rosa profundo
    }

    @api.depends('tag_ids')
    def _compute_tag_colors(self):
        for message in self:
            if message.tag_ids:
                color_blocks = ''.join(
                    f'<span style="display:inline-block;width:15px;height:15px;background-color:{self.COLOR_MAP.get(tag.tag_color, "#FFFFFF")};margin-right:5px;border-radius:3px;"></span>'
                    for tag in message.tag_ids
                )
                message.tag_color = color_blocks
            else:
                message.tag_color = ""
