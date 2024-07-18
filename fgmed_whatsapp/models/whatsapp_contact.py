from odoo import models, fields

class whatsapp_contact(models.Model):
    _name = 'whatsapp_contact'
    _description = 'WhatsApp Contact'

    name = fields.Char(string='Name', required=True)
    waid = fields.Char(string='WA ID')
    active = fields.Boolean(string='Active', default=True)
    tag_ids = fields.Many2many('whatsapp_tag', string='Tags')
