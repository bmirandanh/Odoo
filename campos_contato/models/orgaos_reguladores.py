from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    personal_id = fields.Char(string="RG")#Ocultar quando empresa
    id_regulator = fields.Many2one("fgmed.id.regulators", string="Órgão Expedidor")#Ocultar quando empresa RESTRINGIR CRIAÇÃO NA VIEW
    prefessional_id = fields.Char(string="Registro Profissional")#Ocultar quando empresa
    prefessional_regulator = fields.Many2one("fgmed.professional.regulators", string="Conselho de Classe")#Ocultar quando empresa



class ProfessionalRegulators(models.Model):
     _name = "fgmed.professional.regulators"
     _description = 'Possui nomes de órgãos reguladores de profissões, Ex OAB, CRM ...'

     name = fields.Char(string="Nome - Código")
     description = fields.Char(string="Descrição")


class IdRegulators(models.Model):
     _name = "fgmed.id.regulators"
     _description = 'Possui nomes de órgãos Expedidores, Ex SSP, MINEX ...'

     name = fields.Char(string="Nome - Código")
     description = fields.Char(string="Descrição")

