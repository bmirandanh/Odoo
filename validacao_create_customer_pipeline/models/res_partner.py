from odoo import api, fields, models
from odoo.exceptions import ValidationError
from difflib import SequenceMatcher
import Levenshtein
from Levenshtein import ratio
from odoo.exceptions import UserError
from odoo.tools.translate import _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    skip_validation = fields.Boolean(string="Pular validações", default=False)

    def action_custom_save() :
        pass
    
    @api.model
    def check_for_similar_values(self, model, field_name, field_value, record_id=None):
        if not field_name or not field_value:
            return None

        if len(field_value.strip()) < 3:
            return None

        domain = [(field_name, '=ilike', f"%{field_value}%")]

        if record_id:
            domain.append(('id', '!=', record_id))

        records = self.env[model].search(domain)

        similarity_threshold = 0.8

        for record in records:
            value_to_compare = getattr(record, field_name, '')

            if value_to_compare and ratio(field_value, value_to_compare) >= similarity_threshold:
                return record

        return None

                
    @api.onchange('name', 'email', 'phone')
    def _onchange_check_for_duplicates(self):
        self.ensure_one()
        if not self.skip_validation and (self.name or self.email or self.phone):
            similar_record = self.check_for_similar_values('res.partner', 'name', self.name, self.id)
            if similar_record:
                message = _('Já existe um registro com dados similares (nome: {}, e-mail: {}, telefone: {}).'.format(similar_record.name, similar_record.email, similar_record.phone))
                return {
                    'warning': {
                        'title': _('Aviso!'),
                        'message': message,
                    },
                }

    @api.model
    def check_for_similar_values(self, model_name, field_name, field_value, record_id):
        model = self.env[model_name]
        domain = [(field_name, '=ilike', field_value)]
        if record_id and not isinstance(record_id, models.NewId):
            domain.append(('id', '!=', record_id))
        return model.search(domain, limit=1)
        
    @api.model
    def create(self, vals):
        if not vals.get('skip_validation'):
            name_value = vals.get('name')
            similar_name_records = self.env['res.partner'].search_count([('name', '=', name_value)])
            if similar_name_records > 0:
                message = f"Já existe um registro com o nome '{name_value}' na base de dados. Não é permitido criar um registro com o mesmo nome."
                raise ValidationError(message)
        return super(ResPartner, self).create(vals)

    
    def write(self, vals):
        skip_validation = vals.get('skip_validation', self.skip_validation)
        
        if not skip_validation: 
            for partner in self:
                if vals.get('name'):
                    similar_name_records = self.env['res.partner'].search_count([('name', '=', vals['name']), ('id', '!=', partner.id)])

                    if similar_name_records > 0:
                        message = f"Já existe um registro com o nome '{vals['name']}' na base de dados. Não é permitido criar um registro com o mesmo nome."
                        raise ValidationError(message)

                if vals.get('email') and vals.get('phone'):
                    for partner in self:
                        similar_email_phone_records = self.env['res.partner'].search_count([('email', '=', vals['email']), ('phone', '=', vals['phone']), ('id', '!=', partner.id)])

                        if similar_email_phone_records > 0:
                            message = f"Já existe um registro com o mesmo email e número de telefone na base de dados. Não é permitido criar um registro com valores duplicados."

                            raise ValidationError(message)

            return super(ResPartner, self).write(vals)