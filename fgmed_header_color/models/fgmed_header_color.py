from odoo import fields, models


class fgmedHeaderColor(models.Model):
    _inherit = 'res.config.settings'

    fgmed_header_color = fields.Char(string="Cor do Header")
