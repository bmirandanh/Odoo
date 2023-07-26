from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        vals.update({'is_company': False})
        return super(ResPartner, self).create(vals)