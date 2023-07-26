from odoo import models, fields

class FgmedConfigParams(models.Model):
    _name = "fgmed.config.params"
    _description = "Configurações Chave-valor"
    chave = fields.Char()
    valor = fields.Char()
