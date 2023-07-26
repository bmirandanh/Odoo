from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    l10n_br_cnpj_cpf = fields.Char(
        string='CNPJ/CPF',
        compute='_compute_l10n_br_cnpj_cpf',
        store=True,
        readonly=True
    )

    l10n_br_cnpj_cpf_formatted = fields.Char(
        string='CNPJ/CPF Formatado',
    )
    phone = fields.Char(string='Phone', copy=False, index=True)
    phone_formatted = fields.Char(string='Phone Formatted', compute='_compute_phone_formatted', store=False)

    @api.onchange('l10n_br_cnpj_cpf_formatted')
    def _onchange_l10n_br_cnpj_cpf_formatted(self):
        if self.l10n_br_cnpj_cpf_formatted:
            cnpj_cpf = self.l10n_br_cnpj_cpf_formatted.replace('.', '').replace('/', '').replace('-', '')
            if len(cnpj_cpf) == 11:
                self.l10n_br_cnpj_cpf_formatted = f'{cnpj_cpf[:3]}.{cnpj_cpf[3:6]}.{cnpj_cpf[6:9]}-{cnpj_cpf[9:]}'
            elif len(cnpj_cpf) == 14:
                self.l10n_br_cnpj_cpf_formatted = f'{cnpj_cpf[:2]}.{cnpj_cpf[2:5]}.{cnpj_cpf[5:8]}/{cnpj_cpf[8:12]}-{cnpj_cpf[12:]}'
            else:
                self.l10n_br_cnpj_cpf_formatted = False
    @api.model
    def format_cnpj_cpf(self, cnpj_cpf):
        """Format CNPJ/CPF to display in view"""
        if isinstance(cnpj_cpf, str):
            if len(cnpj_cpf) == 11:
                return f'{cnpj_cpf[:3]}.{cnpj_cpf[3:6]}.{cnpj_cpf[6:9]}-{cnpj_cpf[9:]}'
            elif len(cnpj_cpf) == 14:
                return f'{cnpj_cpf[:2]}.{cnpj_cpf[2:5]}.{cnpj_cpf[5:8]}/{cnpj_cpf[8:12]}-{cnpj_cpf[12:]}'
        return False

    @api.model
    def set_l10n_br_cnpj_cpf(self, value):
        self.l10n_br_cnpj_cpf = value.replace('.', '').replace('-', '').replace('/', '')
    
    @api.depends('l10n_br_cnpj_cpf_formatted')
    def _compute_l10n_br_cnpj_cpf(self):
        for partner in self:
            if partner.l10n_br_cnpj_cpf_formatted:
                partner.l10n_br_cnpj_cpf = partner.l10n_br_cnpj_cpf_formatted.replace('.', '').replace('-', '').replace('/', '')
            else:
                partner.l10n_br_cnpj_cpf = False
    
    @api.onchange('l10n_br_cnpj_cpf')
    def onchange_l10n_br_cnpj_cpf(self):
        if isinstance(self.l10n_br_cnpj_cpf, str):
            self.l10n_br_cnpj_cpf = self.l10n_br_cnpj_cpf.replace('.', '').replace('-', '').replace('/', '')

    def write(self, vals):
        if isinstance(vals.get('l10n_br_cnpj_cpf'), str):
            vals['l10n_br_cnpj_cpf'] = vals['l10n_br_cnpj_cpf'].replace('.', '').replace('-', '').replace('/', '')
        return self.write(vals)
                
    @api.onchange('phone')
    def onchange_phone(self):
        if self.phone:
            self.phone = self.phone.replace('.', '').replace('-', '').replace('(', '').replace(')', '')

    def write(self, vals):
        if vals.get('phone'):
            vals['phone'] = vals['phone'].replace('.', '').replace('-', '').replace('(', '').replace(')', '')
        return super().write(vals)

    @api.depends('phone')
    def _compute_phone_formatted(self):
        for partner in self:
            if partner.phone:
                phone_formatted = partner.phone
                phone_formatted = phone_formatted.replace(' ', '')  # remove espaços em branco
                phone_formatted = phone_formatted.replace(',', ', ')  # insere espaço depois das vírgulas
                phone_formatted = phone_formatted[:2] + ' (' + phone_formatted[2:4] + ') ' + phone_formatted[4:9] + '-' + phone_formatted[9:]
                partner.phone_formatted = phone_formatted
            else:
                partner.phone_formatted = False