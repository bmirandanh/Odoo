from odoo import models, api, exceptions, fields, _
from odoo.exceptions import UserError
import phonenumbers
from phonenumbers import PhoneNumberFormat

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

class ProfessionList(models.Model):
     _name = "fgmed.profession.list"
     _description = 'Possui Lista de profissões do Brasil, conforme a CBO'

     name = fields.Char(string="Nome")
     code = fields.Char(string="Código - CBO")
     type = fields.Char(string="Tipo de registro")


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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    birth_date = fields.Date(string="Data de Nascimento")
    country_origin_id = fields.Many2one("res.country", string="País de Origem")

    personal_id = fields.Char(string="RG")#Ocultar quando empresa
    id_regulator = fields.Many2one("fgmed.id.regulators", string="Órgão Expedidor")#Ocultar quando empresa RESTRINGIR CRIAÇÃO NA VIEW
    professional_id = fields.Char(string="Registro Profissional")#Ocultar quando empresa
    professional_regulator = fields.Many2one("fgmed.professional.regulators", string="Conselho de Classe")#Ocultar quando empresa RESTRINGIR CRIAÇÃO NA VIEW
    profession = fields.Many2one("fgmed.profession.list", string="Profissão")#Profissão

    def _check_and_format_partner_fields(self, vals):
        missing_fields_pt_br = {
            'mobile': 'Celular',
            'phone': 'Telefone',
        }
        for field in ['mobile', 'phone']:
            if vals.get(field):
                if not vals[field].startswith('+'):
                    # Supomos que números sem um prefixo '+' são do Brasil
                    vals[field] = '+55' + vals[field]
                else:
                    # Supomos que números com um prefixo '+' não são do Brasil
                    # Então, removemos qualquer espaço em branco após o '+'
                    vals[field] = '+' + vals[field][1:].lstrip()
                try:
                    number = phonenumbers.parse(vals[field])
                    if not phonenumbers.is_valid_number(number):
                        raise UserError(('O número de %s fornecido não é válido.' % missing_fields_pt_br[field]))
                    else:
                        # Formata o número de telefone para o formato internacional
                        formatted_number = phonenumbers.format_number(number, PhoneNumberFormat.INTERNATIONAL)
                        vals[field] = formatted_number
                except phonenumbers.phonenumberutil.NumberParseException:
                    raise UserError(('Houve uma exceção ao verificar o número %s .- ' % missing_fields_pt_br[field]))

    def write(self, vals):
        if 'l10n_br_cnpj_cpf' in vals and vals['l10n_br_cnpj_cpf'] != False:
            cpf_cnpj = str(vals['l10n_br_cnpj_cpf'])
            cpf_cnpj = cpf_cnpj.replace('-', '').replace('.', '').replace('', '')
            cpf_cnpj.strip()
            vals['l10n_br_cnpj_cpf'] = cpf_cnpj
        if vals.get('mobile') or vals.get('phone'):
            self._check_and_format_partner_fields(vals)
        return super(ResPartner, self).write(vals)

    @api.constrains('l10n_br_cnpj_cpf')
    def _check_cpf_cnpj(self):
        for record in self:
            l10n_br_cnpj_cpf = record.l10n_br_cnpj_cpf
            if l10n_br_cnpj_cpf and  l10n_br_cnpj_cpf != False:
                l10n_br_cnpj_cpf = ''.join(filter(str.isdigit, l10n_br_cnpj_cpf))
                if record.is_company:
                    if not _validate_cnpj(l10n_br_cnpj_cpf):
                        raise exceptions.ValidationError('CNPJ inválido')
                else:
                    if not _validate_cpf(l10n_br_cnpj_cpf):
                        raise exceptions.ValidationError('CPF inválido')

