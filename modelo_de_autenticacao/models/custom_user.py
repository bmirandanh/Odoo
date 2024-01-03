from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import logging
from datetime import datetime, timedelta
import time

_logger = logging.getLogger(__name__)

class CustomAuthUser(models.Model):
    _name = 'custom.auth.user'
    _description = 'Custom Auth User'

    username = fields.Char(string='Nome de Usuário', required=True, index=True, unique=True)
    password = fields.Char(string='Senha')
    username_moodle = fields.Char(string='Nome de Usuário moodle', required=True, index=True, unique=True)
    password_moodle = fields.Char(string='Senha moodle')
    password_hash = fields.Char(string='Hash da Senha', readonly=True)
    email = fields.Char(string='E-mail', required=True, index=True, unique=True)
    fa_secret = fields.Char(string='Segredo do 2FA', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Contato', help='Contato do Aluno no Odoo.')
    image = fields.Image(string ='Imagem do Cadastro' )
    is_admin = fields.Boolean(string="Is Admin", default=False)
    #campo para rastrear a última validação do token 2FA
    last_2fa_validation = fields.Datetime(string='Last 2FA Validation')

    @api.model
    def create(self, vals):
        try:
            # Aqui você pega a senha do dicionário vals e depois gera o hash.
            if 'password' in vals:
                password = vals.pop('password')
                vals['password_hash'] = generate_password_hash(password)
            else:
                raise ValidationError(_('A senha é obrigatória.'))

            if self.search([('username', '=', vals.get('username'))]):
                raise ValidationError(_('O nome de usuário já existe. Por favor, escolha um diferente.'))

            vals['fa_secret'] = pyotp.random_base32()
            new_user = super(CustomAuthUser, self).create(vals)
            
                # Verifica se o usuário deve ser administrador
            if new_user.is_admin:
                # Encontra o grupo de administradores do website
                website_admin_group = self.env.ref('website.group_website_designer')
                
                # Cria um usuário do Odoo vinculado ao usuário personalizado
                odoo_user_vals = {
                    'name': new_user.username,
                    'login': new_user.email,  # ou outro campo apropriado
                    'groups_id': [(4, website_admin_group.id)]
                }
                odoo_user = self.env['res.users'].create(odoo_user_vals)
    
            new_user.send_welcome_email(password)
            return new_user
        except Exception as e:
            _logger.exception("Erro ao criar um novo usuário: %s", e)
            raise

    def write(self, vals):
        try:
            new_password = vals.pop('password')
            _logger.info('new_password: %s', new_password)
            if not new_password:
                raise ValidationError(_('A alteração da senha é obrigatória para atualizações no registro.'))
            else:
                vals['password_hash'] = generate_password_hash(new_password)
            
            existing_user = self.search([('username', '=', vals.get('username', '')), ('id', '!=', self.id)])
            if existing_user:
                raise ValidationError(_('O nome de usuário já existe. Por favor, escolha um diferente.'))
            
            result = super(CustomAuthUser, self).write(vals)
            self.send_data_change_email(new_password)
            
            return result
        except Exception as e:
            _logger.exception("Erro ao atualizar o usuário: %s", e)
            raise
        
    # Função para adicionar o usuário ao grupo de design do website
    def add_to_website_designers_group(self):
        group_website_designer = self.env.ref('website.group_website_designer')
        for user in self:
            if user.is_admin:
                # Cria um usuário do Odoo vinculado ao usuário personalizado, se necessário
                odoo_user = self.env['res.users'].create({
                    'name': user.name,
                    'login': user.email,
                    'password': user.password,  
                    'groups_id': [(4, group_website_designer.id)]
                })
                
    def check_password(self, password):
            # Verifica se a senha fornecida corresponde ao hash armazenado
            return check_password_hash(self.password_hash, password)
        
    def send_token(self, token):
        # Verifica o método preferido e envia o token Implementação do envio do token por e-mail
        try:
            template = self.env.ref('modelo_de_autenticacao.email_template_2fa_token')
            if template:
                # Atualiza o contexto do template com o token
                template_ctx = template.with_context(token=token)
                template_ctx.send_mail(self.id, force_send=True)
            else:
                # Caso não haja um template, você pode criar um e-mail diretamente
                self.env['mail.mail'].create({
                    'subject': 'Seu Token de Autenticação de Dois Fatores',
                    'body_html': '<p>Seu token é: {}</p>'.format(token),
                    'email_to': self.email,
                    'auto_delete': True,
                }).send()
        except Exception as e:
            _logger.error('Falha ao enviar e-mail de token 2FA: %s', e)        
            
    def generate_2fa_token(self):
        # Gera o token TOTP com o segredo do usuário e um intervalo de 300 segundos (5 minutos)
        totp = pyotp.TOTP(self.fa_secret, interval=300)
        token = totp.now()
        # Armazena o token gerado numa variável de instância para validação posterior
        self.env['ir.config_parameter'].sudo().set_param('2fa.token.{}'.format(self.id), token)
        # Envia o token por e-mail
        self.send_token(token)

    def validate_2fa_token(self, token):
        # Valida o token TOTP utilizando o segredo do usuário
        stored_token = self.env['ir.config_parameter'].sudo().get_param('2fa.token.{}'.format(self.id))
        if token == stored_token:
            self.env.cr.execute(
                "UPDATE custom_auth_user SET last_2fa_validation = %s WHERE id = %s",
                (datetime.now(), self.id)
            )
            # Remove o token armazenado após a validação bem-sucedida
            self.env['ir.config_parameter'].sudo().set_param('2fa.token.{}'.format(self.id), False)
            return True
        return False

    def is_token_valid(self):
        self.ensure_one()
        # Verifica se o último token 2FA validado ainda é válido dentro de 1 hora
        last_validation = self.read(['last_2fa_validation'])[0].get('last_2fa_validation')
        if last_validation and datetime.now() < last_validation + timedelta(hours=1):
            return True
        return False

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
                    template_ctx = template.with_context({
                        'new_password': new_password,
                    })
                    template_ctx.send_mail(self.id, force_send=True)
            except Exception as e:
                _logger.exception("Erro ao enviar e-mail de notificação de alteração: %s", e)