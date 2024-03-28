from odoo import models, fields, api
from odoo.exceptions import ValidationError
from lxml import etree

class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_br_cnpj_cpf_formatted = fields.Char(
        compute='_compute_l10n_br_cnpj_cpf_formatted',
        string='CNPJ/CPF Formatado',
        store=False
    )

    @api.depends('l10n_br_cnpj_cpf')
    def _compute_l10n_br_cnpj_cpf_formatted(self):
        for partner in self:
            partner.l10n_br_cnpj_cpf_formatted = self.format_cnpj_cpf(partner.l10n_br_cnpj_cpf)

    @staticmethod
    def format_cnpj_cpf(cnpj_cpf):
        if cnpj_cpf:
            cnpj_cpf = re.sub('[^0-9]', '', cnpj_cpf)
            if len(cnpj_cpf) == 11:
                return f'{cnpj_cpf[:3]}.{cnpj_cpf[3:6]}.{cnpj_cpf[6:9]}-{cnpj_cpf[9:]}'
            elif len(cnpj_cpf) == 14:
                return f'{cnpj_cpf[:2]}.{cnpj_cpf[2:5]}.{cnpj_cpf[5:8]}/{cnpj_cpf[8:12]}-{cnpj_cpf[12:]}'
            else:
                raise ValidationError('CNPJ/CPF inválido')
        else:
            return False


    def fields_view_get_format(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResPartner, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='l10n_br_cnpj_cpf']"):
                if node.get('name'):
                    name = 'l10n_br_cnpj_cpf_formatted'
                    node.set('name', name)
            res['arch'] = etree.tostring(doc)
        return res