from odoo import models, api, _
from odoo import exceptions
from odoo.exceptions import UserError
import phonenumbers
from phonenumbers import PhoneNumberFormat

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
    @api.onchange('phone', 'mobile')
    def _check_phone_and_mobile(self):
        if self.sale_order_count > 0:
            if (not self.phone and not self.mobile) or \
               (self._origin.phone and not self.phone and not self.mobile) or \
               (self._origin.mobile and not self.mobile and not self.phone):
                raise exceptions.UserError(_('Este parceiro tem um pedido de venda associado. Telefone e celular não podem ficar vazios.'))
        
        if self.phone:
            self._check_and_format_partner_fields({'phone': self.phone})
        if self.mobile:
            self._check_and_format_partner_fields({'mobile': self.mobile})

    @api.model
    def create(self, vals):
        if vals.get('mobile') or vals.get('phone'):
            self._check_and_format_partner_fields(vals)
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        for record in self:
            if record.sale_order_count > 0:
                if ('phone' in vals and not vals['phone'] or 'phone' not in vals and not record.phone) \
                    and ('mobile' in vals and not vals['mobile'] or 'mobile' not in vals and not record.mobile):
                    raise UserError(_('Este parceiro tem um pedido de venda associado. Telefone e celular não podem ficar vazios.'))
            if vals.get('mobile') or vals.get('phone'):
                self._check_and_format_partner_fields(vals)
        return super(ResPartner, self).write(vals)

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
