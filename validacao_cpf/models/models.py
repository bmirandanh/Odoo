from odoo import models, api, exceptions, fields

def _validate_cpf(l10n_br_cnpj_cpf):
    if len(l10n_br_cnpj_cpf) != 11:
        return False
    if l10n_br_cnpj_cpf in ['00000000000', '11111111111', '22222222222', '33333333333', '44444444444', '55555555555', '66666666666', '77777777777', '88888888888', '99999999999']:
        return False
    soma = 0
    for i in range(9):
        soma += int(l10n_br_cnpj_cpf[i]) * (10 - i)
    resto = 11 - (soma % 11)
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(l10n_br_cnpj_cpf[9]):
        return False
    soma = 0
    for i in range(10):
        soma += int(l10n_br_cnpj_cpf[i]) * (11 - i)
    resto = 11 - (soma % 11)
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(l10n_br_cnpj_cpf[10]):
        return False
    return True


def _validate_cnpj(l10n_br_cnpj_cpf):
    if len(l10n_br_cnpj_cpf) != 14:
        return False
    if l10n_br_cnpj_cpf in ['00000000000000', '11111111111111', '22222222222222', '33333333333333', '44444444444444', '55555555555555', '66666666666666', '77777777777777', '88888888888888', '99999999999999']:
        return False
    multiplicadores_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    multiplicadores_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = 0
    for i in range(12):
        soma += int(l10n_br_cnpj_cpf[i]) * multiplicadores_1[i]
    resto = soma % 11
    digito_1 = 0 if resto < 2 else 11 - resto
    soma = 0
    for i in range(13):
        soma += int(l10n_br_cnpj_cpf[i]) * multiplicadores_2[i]
    resto = soma % 11
    digito_2 = 0 if resto < 2 else 11 - resto
    if digito_1 != int(l10n_br_cnpj_cpf[12]) or digito_2 != int(l10n_br_cnpj_cpf[13]):
        return False
    return True

class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_br_cnpj_cpf = fields.Char(string='CPF/CNPJ')

    @api.onchange('is_company')
    def _onchange_is_company(self):
        if self.is_company:
            self.l10n_br_cnpj_cpf = 'CNPJ'
        else:
            self.l10n_br_cnpj_cpf = 'CPF'

    @api.constrains('l10n_br_cnpj_cpf')
    def _check_cpf_cnpj(self):
        for record in self:
            l10n_br_cnpj_cpf = record.l10n_br_cnpj_cpf
            if l10n_br_cnpj_cpf:
                l10n_br_cnpj_cpf = ''.join(filter(str.isdigit, l10n_br_cnpj_cpf))
                if record.is_company:
                    if not _validate_cnpj(l10n_br_cnpj_cpf):
                        raise exceptions.ValidationError('CNPJ inválido')
                else:
                    if not _validate_cpf(l10n_br_cnpj_cpf):
                        raise exceptions.ValidationError('CPF inválido')