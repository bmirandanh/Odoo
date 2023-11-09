from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from werkzeug.security import generate_password_hash
import pyotp
import logging

_logger = logging.getLogger(__name__)

class CustomAuthUser(models.Model):
    _name = 'custom.auth.user'
    _description = 'Custom Auth User'

    username = fields.Char(string='Nome de Usuário', required=True, index=True, unique=True)
    password = fields.Char(string='Senha')
    password_hash = fields.Char(string='Hash da Senha', readonly=True)
    email = fields.Char(string='E-mail', required=True, index=True, unique=True)
    fa_secret = fields.Char(string='Segredo do 2FA', readonly=True)

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