# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo import exceptions
from odoo.exceptions import UserError
import phonenumbers
from phonenumbers import PhoneNumberFormat


class FgmedLeadProduct(models.Model):
    _inherit = "crm.lead"

    l10n_br_number = fields.Char(string='Número')
    l10n_br_district = fields.Char(string='Bairro')
    city_id = fields.Many2one('res.city', string='Cidade')
    crm_course_id = fields.Many2one('product.template', string='Curso de interesse')
    crm_variant_id = fields.Many2one('product.product', string='Variante de interesse')
    
    
    @api.model
    def create(self, vals):
        if not vals.get('mobile') and not vals.get('phone'):
            raise exceptions.UserError(_('Telefone e celular não podem ficar vazios. Pelo menos um deles deve ser preenchido.'))
        if vals.get('mobile') or vals.get('phone'):
            self._check_and_format_partner_fields(vals)
        return super().create(vals)

    def write(self, vals):
        for record in self:
            if (not vals.get('mobile') and not vals.get('phone')) and (not record.mobile and not record.phone):
                raise exceptions.UserError(_('Telefone e celular não podem ficar vazios. Pelo menos um deles deve ser preenchido.'))
            if vals.get('mobile') or vals.get('phone'):
                self._check_and_format_partner_fields(vals)
        return super().write(vals)

    def _check_and_format_partner_fields(self, vals):
        missing_fields_pt_br = {
            'mobile': 'Telefone móvel',
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
                        raise UserError(_('O número de %s fornecido não é válido.' % missing_fields_pt_br[field]))
                    else:
                        # Formata o número de telefone para o formato internacional
                        formatted_number = phonenumbers.format_number(number, PhoneNumberFormat.INTERNATIONAL)
                        vals[field] = formatted_number
                except phonenumbers.phonenumberutil.NumberParseException:
                    raise UserError(_('O número de %s fornecido não é válido.' % missing_fields_pt_br[field]))