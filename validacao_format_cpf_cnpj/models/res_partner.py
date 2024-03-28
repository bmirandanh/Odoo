from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Add the new field to store the placeholder value
    l10n_br_cnpj_cpf_placeholder = fields.Char('CNPJ/CPF Placeholder', compute='_compute_cnpj_cpf_placeholder')

    @api.depends('l10n_br_legal_name')
    def _compute_cnpj_cpf_placeholder(self):
        for partner in self:
            if partner.is_company:
                partner.l10n_br_cnpj_cpf_placeholder = 'CNPJ'
            else:
                partner.l10n_br_cnpj_cpf_placeholder = 'CPF'

    # Update the placeholder value when the l10n_br_legal_name field is changed
    @api.onchange('l10n_br_legal_name')
    def onchange_l10n_br_legal_name(self):
        for partner in self:
            if partner.l10n_br_cnpj_cpf_placeholder:
                partner.l10n_br_cnpj_cpf = ''
                self.env['ir.ui.view'].sudo().clear_caches()
