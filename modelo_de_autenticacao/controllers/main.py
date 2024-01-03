from odoo import http
from odoo.http import request
import pyotp
from odoo import tools
import logging
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime, timedelta
import time
import pdfkit
from odoo import api, fields, models
import base64
from odoo.http import request
import requests
import re
from lxml import html

_logger = logging.getLogger(__name__)


class MoodleAccessController(http.Controller):
    
    @http.route('/moodle_access', type='http', auth="public", website=True)
    def moodle_access(self, **kw):
        # Obtendo ID do usuário customizado da sessão
        custom_auth_user_id = request.session.get('custom_auth_user_id')
        if not custom_auth_user_id:
            _logger.info("Nenhum ID de autenticação customizada encontrado na sessão.")
            return request.redirect('/web/login')

        # Busca o usuário customizado no banco de dados
        custom_user = request.env['custom.auth.user'].sudo().browse(custom_auth_user_id)
        if not custom_user.exists():
            _logger.info("Usuário customizado não encontrado na base de dados.")
            return request.redirect('website.404')

        # Obtendo o token do Moodle
        token = self.get_moodle_token()
        if not token:
            _logger.error("Falha ao obter o token do Moodle.")
            return request.redirect('website.404')

        # Obtendo a URL de login do Moodle
        login_url = self.get_moodle_login_url(custom_user, token)
        if not login_url:
            _logger.error(f'Falha ao obter a URL de login do Moodle para o usuário: {custom_user.username}')
            return request.redirect('website.404')

        # Redireciona o usuário para o Moodle
        return request.redirect(login_url)

    def get_moodle_token(self):
        custom_auth_user_id = request.session.get('custom_auth_user_id')
        custom_user = request.env['custom.auth.user'].sudo().browse(custom_auth_user_id)
        username = custom_user.username_moodle
        password = custom_user.password_moodle
        service = 'moodle_api'
        domainname = 'https://avadev.medflix.club'

        login_url = f'{domainname}/login/token.php?username={username}&password={password}&service={service}'
        try:
            response = requests.get(login_url)
            if response.status_code == 200:
                response_data = response.json()
                if 'token' in response_data:
                    _logger.info("Token obtido com sucesso.")
                    return response_data['token']
                else:
                    _logger.error(f"Resposta do Moodle não contém token: {response_data}")
                    return None
            else:
                _logger.error(f"Resposta HTTP não bem-sucedida: Status {response.status_code}")
                return None
        except Exception as e:
            _logger.exception(f"Exceção ao fazer requisição de token: {e}")
            return None

    def get_moodle_login_url(self, custom_user, token):
        domainname = 'http://MOODLE_WWW_ROOT'
        functionname = 'auth_userkey_request_login_url'
        serverurl = f'{domainname}/webservice/rest/server.php?wstoken={token}&wsfunction={functionname}&moodlewsrestformat=json'

        # Parâmetros para criar/atualizar o usuário no Moodle e obter a URL de login
        param = {
            'user': {
                'firstname': custom_user.firstname,  # Nome do usuário
                'lastname': custom_user.lastname,    # Sobrenome do usuário
                'username': custom_user.username,    # Nome de usuário no Moodle
                'email': custom_user.email,          # E-mail do usuário
            }
        }

        try:
            response = requests.post(serverurl, json=param)
            resp_content = response.json()
            if resp_content and 'loginurl' in resp_content:
                _logger.info("URL de login do Moodle obtida com sucesso.")
                return resp_content['loginurl']
        except Exception as e:
            _logger.exception(f"Exceção ao obter a URL de login do Moodle: {e}")
            return None

class CustomAuthController(http.Controller):

    @http.route('/web/2flogin', type='http', auth="public", methods=['GET'], website=True)
    def web_login(self, **kw):
        _logger.info('Accessed 2-factor login page.')
        return request.render('modelo_de_autenticacao.login_template', {
            'csrf_token': request.csrf_token()
        })

    @http.route('/web/2flogin', type='http', auth="public", methods=['POST'], website=True)
    def web_login_post(self, **post):
        username = post.get('username')
        password = post.get('password')
        _logger.info('Tentativa de login para o usuário: %s', username)
        users = request.env['custom.auth.user'].sudo().search([('username', '=', username)], limit=1)

        if users and users.check_password(password):
            user = users[0]  # Assume que a busca pelo usuário é única devido ao 'limit=1'
            _logger.info('Senha verificada para o usuário: %s', username)
            user.generate_2fa_token()  # Gera e envia o token por e-mail
            return request.render('modelo_de_autenticacao.2fa_template', {'user': user})
        else:
            _logger.warning('Login falhou para o usuário: %s', username)
            return request.render('modelo_de_autenticacao.login_template', {'error': 'Credenciais inválidas'})

    @http.route('/web/2fa', type='http', auth="public", methods=['POST'], website=True)
    def web_2fa_post(self, **post):
        user_id = post.get('user_id')
        token = post.get('token')
        _logger.info('Token 2FA recebido para o ID do usuário: %s', user_id)
        user = request.env['custom.auth.user'].sudo().browse(int(user_id))
        
        if user.validate_2fa_token(token):
            _logger.info('Token 2FA validado para o ID do usuário: %s', user_id)
            request.session['custom_auth_user_id'] = user.id
            return http.redirect_with_hash('/minha/pagina_protegida')
        
        else:
            _logger.warning('Validação do token 2FA falhou para o ID do usuário: %s', user_id)
            request.session['login_error'] = 'Token incorreto ou expirado'
            return http.redirect_with_hash('/web/2flogin')
        
    @http.route('/minha/pagina_protegida', type='http', auth="public", website=True)
    def protected_page(self, **kw):
        # Primeiro, obtenha o ID do usuário autenticado da sessão
        custom_auth_user_id = request.session.get('custom_auth_user_id')
        
        if not custom_auth_user_id:
            _logger.warning('No Custom Auth User ID found in session, redirecting to login.')
            return redirect('/web/2flogin')

        # Agora que temos o ID, podemos buscar o usuário
        custom_user = request.env['custom.auth.user'].sudo().browse(custom_auth_user_id)

        if not custom_user.exists():
            _logger.error('Custom Auth User not found, redirecting to login.')
            return redirect('/web/2flogin')

        # Verifique se o usuário tem um parceiro associado
        if not custom_user.partner_id:
            _logger.error('No partner associated with Custom Auth User ID: %s', custom_auth_user_id)
            return request.redirect('website.404')

        # Verifique se o token 2FA ainda é válido
        if not custom_user.is_token_valid():
            _logger.warning('Token expired or not valid, redirecting to login.')
            return redirect('/web/2flogin')

        # Se tudo estiver correto, renderize a página protegida
        _logger.info('Rendering protected page for Custom Auth User ID: %s', custom_auth_user_id)
        return request.render('modelo_de_autenticacao.protected_page_template', {
            'custom_user': custom_user
        })

    # Define uma rota para o registro acadêmico que pode ser acessada publicamente no website.
    @http.route(['/academic_record'], type='http', auth="public", website=True)
    def academic_record(self, **kw):
        # Obtém o ID do usuário autenticado personalizado da sessão.
        custom_auth_user_id = request.session.get('custom_auth_user_id')

        # Se não houver um usuário autenticado na sessão, redireciona para a página de login.
        if not custom_auth_user_id:
            return http.redirect_with_hash('/web/2flogin')

        # Busca o usuário personalizado usando o ID obtido da sessão.
        custom_user = request.env['custom.auth.user'].sudo().browse(custom_auth_user_id)

        # Se o usuário personalizado não existir ou não tiver um parceiro associado, redireciona para a página de login.
        if not custom_user.exists() or not custom_user.partner_id:
            return http.redirect_with_hash('/web/2flogin')

        # Busca todas as matrículas associadas ao parceiro do usuário personalizado.
        matriculas = request.env['informa.matricula'].sudo().search([('nome_do_aluno', '=', custom_user.partner_id.id)])

        # Cria um dicionário para armazenar os registros de disciplina.
        registros_disciplina = {}
        # Itera sobre todas as matrículas e disciplinas associadas, buscando os registros de disciplina.
        for matricula in matriculas:
            for disciplina in matricula.curso.grupo_disciplina_id.disciplina_ids:
                registros_disciplina[disciplina.id] = request.env['informa.registro_disciplina'].sudo().search(
                    [('aluno_id', '=', matricula.nome_do_aluno.id),
                     ('disciplina_id', '=', disciplina.id),
                     ('curso_id', '=', matricula.curso.id)], limit=1)

        # Renderiza o template com as informações necessárias.
        return request.render('modelo_de_autenticacao.academic_record_template', {
            'partner': custom_user.partner_id,  # Passa o parceiro do usuário personalizado.
            'matriculas': matriculas,           # Passa as matrículas encontradas.
            'registros_disciplina': registros_disciplina,  # Passa os registros de disciplina.
            'custom_user': custom_user,         # Passa o usuário personalizado.
        })

    # Controlador para gerar o PDF do registro acadêmico
    @http.route('/academic_record/pdf', type='http', auth="public", website=True)
    def academic_record_pdf(self, **kw):
        # Obtém o ID do usuário autenticado personalizado da sessão
        custom_auth_user_id = request.session.get('custom_auth_user_id')

        # Se não houver um usuário autenticado na sessão, redireciona para a página de login
        if not custom_auth_user_id:
            return request.redirect('/web/login')

        # Busca o usuário personalizado usando o ID obtido da sessão
        custom_user = request.env['custom.auth.user'].sudo().browse(custom_auth_user_id)

        # Certifique-se de que o custom_user existe
        if not custom_user.exists():
            return request.redirect('website.404')

        # Busca todas as matrículas associadas ao parceiro do usuário personalizado
        matriculas = request.env['informa.matricula'].sudo().search([('nome_do_aluno', '=', custom_user.partner_id.id)])
        
        # Cria um dicionário para armazenar os registros de disciplina.
        registros_disciplina = {}
        # Itera sobre todas as matrículas e disciplinas associadas, buscando os registros de disciplina.
        for matricula in matriculas:
            for disciplina in matricula.curso.grupo_disciplina_id.disciplina_ids:
                registros_disciplina[disciplina.id] = request.env['informa.registro_disciplina'].sudo().search(
                    [('aluno_id', '=', matricula.nome_do_aluno.id),
                     ('disciplina_id', '=', disciplina.id),
                     ('curso_id', '=', matricula.curso.id)], limit=1)

        # Obter a ação de relatório e gerar o PDF
        report = request.env.ref('modelo_de_autenticacao.action_report_academic_record')
        data = {
            'partner': custom_user.partner_id,
            'matriculas': matriculas,
            'custom_user': custom_user,
            'registros_disciplina': registros_disciplina,  
        }
        pdf, _ = report.sudo()._render_qweb_pdf([custom_user.id], data=data)

        # Configurar cabeçalhos HTTP para download do PDF
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename="Histórico.pdf"')
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
