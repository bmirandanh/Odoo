from odoo import models, api, _
from odoo.exceptions import UserError
import phonenumbers  # Biblioteca para validar números de telefone

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            self._check_partner_fields(partner)
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        if 'partner_id' in vals:
            for order in self:
                partner = self.env['res.partner'].browse(vals['partner_id'])
                order._check_partner_fields(partner)
        return super(SaleOrder, self).write(vals)

    def _check_partner_fields(self, partner):
        user_name = self.env.user.name  # Defina o user_name aqui

        required_fields = ['street', 'l10n_br_number', 'l10n_br_district', 'zip', 'city_id', 'state_id', 'l10n_br_cnpj_cpf']
        phone_fields = {'phone': phonenumbers.PhoneNumberType.FIXED_LINE, 'mobile': phonenumbers.PhoneNumberType.MOBILE}
        
        # Defina missing_fields_pt_br aqui
        missing_fields_pt_br = {
            'street': 'Rua',
            'l10n_br_number': 'Número',
            'l10n_br_district': 'Bairro',
            'zip': 'CEP',
            'city_id': 'Cidade',
            'state_id': 'Estado',
            'mobile': 'Telefone móvel',
            'phone': 'Telefone fixo',
            'l10n_br_cnpj_cpf': 'CNPJ/CPF',
        }

        missing_fields = [field for field in required_fields if not getattr(partner, field)]
        missing_phone_fields = [field for field in phone_fields if not getattr(partner, field)]
        
        if len(missing_phone_fields) == len(phone_fields):
            missing_fields.extend(missing_phone_fields)
        
        if missing_fields:
            missing_fields_translated = [missing_fields_pt_br[field] for field in missing_fields]
            raise UserError(_('Prezado(a) %s,\n\nIdentificamos que os seguintes campos estão faltando no cadastro do cliente:\n %s.\nPor gentileza, preencha esses campos antes de prosseguir com a venda.\n\nAtenciosamente.' % (user_name, '\n'.join(missing_fields_translated))))
        
        for field, number_type in phone_fields.items():
            number = getattr(partner, field)
            if number:
                try:
                    parsed_number = phonenumbers.parse(number, 'BR')
                    if not phonenumbers.is_valid_number(parsed_number) or phonenumbers.number_type(parsed_number) != number_type:
                        raise UserError(_('Prezado(a) %s,\n\nO número de %s fornecido não é válido ou é do tipo errado. O tipo se refere à natureza do número de telefone: fixo ou móvel. Por gentileza, forneça um número válido e do tipo correto antes de prosseguir com a venda.\n\nAtenciosamente.' % (user_name, missing_fields_pt_br[field])))
                except phonenumbers.phonenumberutil.NumberParseException:
                    raise UserError(_('Prezado(a) %s,\n\nO número de %s fornecido não é válido. Por gentileza, forneça um número válido antes de prosseguir com a venda.\n\nAtenciosamente.' % (user_name, missing_fields_pt_br[field])))
