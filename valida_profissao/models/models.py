from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    profession_id = fields.Many2one('res.profession', string='Profissão')