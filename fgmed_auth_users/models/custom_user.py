from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from datetime import datetime, timedelta
import secrets
import hashlib


_logger = logging.getLogger(__name__)

class CustomAuthUser(models.Model):
    _name = 'custom.auth.user'
    _description = 'Custom Auth User'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    username = fields.Char(string='Nome de Usuário', required=True, index=True, unique=True, tracking=True)
    password = fields.Char(string='Senha', tracking=True)
    password_hash = fields.Char(string='Hash da Senha', readonly=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string="Aluno", help='Contato do Aluno no Odoo.', required=True, tracking=True, domain=[('aluno', '=', True)])
    image = fields.Image(string='Imagem do Cadastro', tracking=True)
    reset_password_token = fields.Char(string='Reset Token', readonly=True, tracking=True)
    reset_password_token_expiration = fields.Datetime(string='Tempo do Token', readonly=True, tracking=True)
    company_id = fields.Many2one('res.company', compute='_compute_company_id', string='Empresa')
    medflix_option = fields.Boolean(string='MedFlix', default=False, tracking=True)
    moodle_option = fields.Boolean(string='Moodle', default=True, tracking=True)
    token = fields.Char(string='Token de Acesso', readonly=True, index=True, unique=True, tracking=True)

    @api.constrains('medflix_option', 'moodle_option')
    def _check_platform_selection(self):
        for record in self:
            if not record.medflix_option and not record.moodle_option:
                raise ValidationError("Pelo menos uma plataforma deve ser selecionada: MedFlix ou Moodle.")
    
    @api.depends()
    def _compute_company_id(self):
        for record in self:
            record.company_id = self.env.company

    @api.model
    def create(self, vals):
        if 'password' in vals:
            password = vals.pop('password')
            vals['password_hash'] = generate_password_hash(password)
        else:
            raise ValidationError(_('A senha é obrigatória.'))
        
        if self.search([('username', '=', vals.get('username'))]):
            raise ValidationError(_('O nome de usuário já existe. Por favor, escolha um diferente.'))
        
        # Gerar um token SHA256 único para o novo usuário
        token = hashlib.sha256(secrets.token_bytes(64)).hexdigest()
        while self.search_count([('token', '=', token)]) > 0:
            # Se o token já existir, gerar um novo
            token = hashlib.sha256(secrets.token_bytes(64)).hexdigest()
        vals['token'] = token
        
        new_user = super(CustomAuthUser, self).create(vals)
        new_user.send_welcome_email(password)
        return new_user

    def write(self, vals):
        # Verifica se a senha está sendo atualizada e processa adequadamente
        if 'password' in vals:
            new_password = vals.pop('password')
            vals['password_hash'] = generate_password_hash(new_password)
            self.send_data_change_email(new_password)

        # Verifica se o nome de usuário está sendo alterado para um já existente
        if 'username' in vals and self.search([('username', '=', vals['username']), ('id', '!=', self.id)]):
            raise ValidationError(_('O nome de usuário já existe. Por favor, escolha um diferente.'))
        
        return super(CustomAuthUser, self).write(vals)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def send_welcome_email(self, password):
        try:
            template = self.env.ref('modelo_de_autenticacao.email_template_welcome', raise_if_not_found=False)
            if template:
                template.with_context({'password': password}).send_mail(self.id, force_send=True)
        except Exception as e:
            _logger.exception("Erro ao enviar e-mail de boas-vindas: %s", e)

    def send_data_change_email(self, new_password):
        try:
            template = self.env.ref('modelo_de_autenticacao.email_template_data_change', raise_if_not_found=False)
            if template:
                template.with_context({'new_password': new_password}).send_mail(self.id, force_send=True)
        except Exception as e:
            _logger.exception("Erro ao enviar e-mail de notificação de alteração: %s", e)
