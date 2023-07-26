from odoo import api, fields, models
import re

class ResPartner(models.Model):
    _inherit = "res.partner"

    birth_date = fields.Date(string="Data de Nascimento")
    #rg = fields.Char(string="RG", size=14)
    #profession = fields.Char(string="Profissão")
    country_origin_id = fields.Many2one("res.country", string="País de Origem")

    @api.constrains("rg")
    def _check_rg(self):
        for record in self:
            
            rg = self.rg
            rg = re.sub('[^0-9]', '', rg)

            # Verifica o comprimento do RG
            if len(rg) != 9:
                return False

            # Verifica se todos os dígitos são iguais (ex: 111111111, 222222222, ...)
            if len(set(rg)) == 1:
                return False

            # Cálculo do dígito verificador
            weight = [2, 3, 4, 5, 6, 7, 8, 9]
            sum_product = sum(int(digit) * weight[i] for i, digit in enumerate(rg[:8]))

            remainder = sum_product % 11
            check_digit = 11 - remainder if remainder >= 2 else 0

            return int(rg[-1]) == check_digit
            pass
