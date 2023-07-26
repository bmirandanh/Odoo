from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    crm = fields.Char(string='CRM')