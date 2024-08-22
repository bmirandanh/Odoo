from odoo import models, fields, api

class WhatsappTag(models.Model):
    _name = 'whatsapp_tag'
    _description = 'WhatsApp Tag'

    name = fields.Char(string='Name', required=True)
    tag_color = fields.Integer(string='Color')  # Campo para armazenar a cor

    importance_level = fields.Selection(
        [
            ('0', 'Comum'),
            ('1', 'Baixa Importância'),
            ('2', 'Importância Moderada'),
            ('3', 'Importância Relevante'),
            ('4', 'Importância Considerável'),
            ('5', 'Importante'),
            ('6', 'Alta Importância'),
            ('7', 'Urgente'),
            ('8', 'Muito Urgente'),
            ('9', 'Crítica'),
            ('10', 'Emergência Máxima'),
        ],
        string='Importance Level',
        required=True,
        default='0'
    )

    COLOR_MAP = {
        '0': 0,   # Branco
        '1': 1,   # Rosa claro
        '2': 2,   # Salmão claro
        '3': 3,   # Dourado
        '4': 4,   # Azul claro
        '5': 5,   # Ameixa
        '6': 6,   # Laranja avermelhado
        '7': 7,   # Azul dócil
        '8': 8,   # Verde lima
        '9': 9,   # Azul violeta
        '10': 10  # Rosa profundo
    }

    @api.onchange('importance_level')
    def _onchange_importance_level(self):
        if self.importance_level:
            self.tag_color = self.COLOR_MAP.get(self.importance_level)
