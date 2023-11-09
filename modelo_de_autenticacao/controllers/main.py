from odoo import http
from odoo.http import request
import pyotp
from odoo import tools
import logging
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from werkzeug.utils import redirect
from odoo import http
import requests

_logger = logging.getLogger(__name__)

class CustomAuthController(http.Controller):
    
    # Rota para exibir a página de login
    @http.route('/web/2flogin', type='http', auth="none", methods=['GET'], website=True)
    def web_login(self, **kw):
        # Garante que o contexto inclui o token CSRF
        return http.request.render('modelo_de_autenticacao.login_template', {
            'csrf_token': http.request.csrf_token()
        })

    # Rota para processar a submissão do formulário de login
    @http.route('/web/2flogin', type='http', auth="none", methods=['POST'], website=True)
    def web_login_post(self, **post):
        username = post.get('username')
        _logger.info('username: %s', username)
        password = post.get('password')
        _logger.info('password: %s', password)
        # Procura o usuário pelo nome de usuário
        user = request.env['custom.auth.user'].sudo().search([('username', '=', username)])
        
        # Se o usuário existe e a senha está correta
        if user and user.check_password(post['password']):
            # Usuário encontrado e senha correspondente
            # Gera e envia o token 2FA
            secret = user.fa_secret
            totp = pyotp.TOTP(secret)
            token = totp.now()
            # Envia o token via e-mail ou SMS
            user.send_token(token)
            # Renderiza a página para inserir o token 2FA
            return http.request.render('modelo_de_autenticacao.2fa_template', {'user': user})
        else:
            # Usuário não encontrado ou senha incorreta
            # Renderiza novamente a página de login com um erro
            return http.request.render('modelo_de_autenticacao.login_template', {'error': 'Credenciais inválidas'})

    # Rota para processar a submissão do formulário 2FA
    @http.route('/web/2fa', type='http', auth="none", methods=['POST'], website=True)
    def web_2fa_post(self, **post):
        user_id = post.get('user_id')
        token = post.get('token')
        
        if not user_id:
            return http.request.render('modelo_de_autenticacao.2fa_template', {
                'error': 'Usuário não encontrado ou sessão expirada.',
                'user': False
            })
        
        user = request.env['custom.auth.user'].sudo().browse(int(user_id))
        
        # Se o usuário existe e o token 2FA é válido
        if user and user.validate_2fa_token(token):
            # Token é válido, cria uma sessão e redireciona para a página protegida
            request.session['custom_auth_user_id'] = user.id
            return redirect('/minha/pagina_protegida')
        else:
            # Token é inválido
            # Renderiza novamente a página 2FA com um erro
            return http.request.render('modelo_de_autenticacao.2fa_template', {'user': user, 'error': 'Token inválido'})

    # Rota para acessar a página protegida
    @http.route('/minha/pagina_protegida', type='http', auth="public", website=True)
    def protected_page(self, **kw):
        # Verifica se o ID do usuário está na sessão
        if not request.session.get('custom_auth_user_id'):
            # Se não estiver, redireciona para a página de login
            return redirect('/web/2flogin')
        
        # Se estiver, renderiza a página protegida
        return http.request.render('modelo_de_autenticacao.protected_page_template', {})