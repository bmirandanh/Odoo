from odoo import http
from odoo.http import request
import pyotp
from odoo import tools
import logging
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.wrappers import Response
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
import xmlrpc.client
from bs4 import BeautifulSoup
import json
import secrets
import werkzeug
from werkzeug.exceptions import BadRequest


_logger = logging.getLogger(__name__)


class MoodleAccessController(http.Controller):
    
    @http.route('/api/verify_token', type='json', auth='public', methods=['POST', 'OPTIONS'], cors='*')
    def verify_token(self, **kwargs):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Tratar solicitações de simulação (OPTIONS)
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)

        data = request.jsonrequest
        token = data.get('token')

        if not token:
            return {'isValid': False}

        user = request.env['custom.auth.user'].sudo().search([('token', '=', token)], limit=1)
        if not user:
            return {'isValid': False}

        # Se o token for válido
        return {'isValid': True}
    
    @http.route('/api/custom_auth_user/check_credentials2', type='json', auth='public', methods=['POST', 'OPTIONS'], cors='*')
    def check_credentials_and_get_token(self, **kwargs):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        data = request.jsonrequest
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {'error': 'Both username and password are required.'}

        user = request.env['custom.auth.user'].sudo().search([('username', '=', username)], limit=1)
        if user and user.check_password(password):
            _logger.info(f"User authenticated: {username}")
            return {'result': True, 'token': user.token}
        else:
            _logger.info(f"Authentication failed for user: {username}")
            return {'result': False}
        
    @http.route('/api/custom_auth_user/check_credentials', type='json', auth='public', methods=['POST'], cors='*')
    def check_credentials2(self):
        try:
            data = request.jsonrequest
            username = data.get('username')
            password = data.get('password')
            if not username or not password:
                return {'error': 'Both username and password are required.'}, 400
            user = request.env['custom.auth.user'].sudo().search([('username', '=', username)], limit=1)
            if user and user.moodle_option:  # Verifica se o usuário existe e se a opção do Moodle está ativada
                _logger.info(f"Username: {username}")
                if user.check_password(password):  # Supondo que exista um método para verificar a senha
                    _logger.info("Usuário deve ser autenticado.")
                    return {'result': True}
                else:
                    _logger.info("Senha incorreta.")
                    return {'result': False}
            else:
                _logger.info("Usuário não encontrado ou acesso ao Moodle desativado.")
                return {'result': False}
        except Exception as e:
            _logger.exception("Erro na API check_credentials: %s", e)
            return {'error': 'Internal Server Error.'}, 500
        
class CustomAuthController(http.Controller):

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
        return request.render('fgmed_auth_users.academic_record_template', {
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
        report = request.env.ref('fgmed_auth_users.action_report_academic_record')
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

    @http.route('/request_reset_password', type='http', auth='public', website=True)
    def request_reset_password(self, **post):
        if request.httprequest.method == 'GET':
            return request.render('fgmed_auth_users.template_request_reset_password')
        elif request.httprequest.method == 'POST':
            email = post.get('email')
            if email:
                # Aqui você pode inserir a lógica para verificar se o e-mail existe e retornar uma mensagem apropriada
                return self.reset_password(**post)
            else:
                return request.render('fgmed_auth_users.template_request_reset_password', {
                    'error': 'Por favor, insira um endereço de e-mail.'
                })

    @http.route('/reset_password', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def reset_password(self, **post):
        email = post.get('email')
        if email:
            partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
            if partner:
                user = request.env['custom.auth.user'].sudo().search([('partner_id', '=', partner.id)], limit=1)
                if user and not user.moodle_option:
                    # Se a opção Moodle estiver desativada, retornar uma mensagem de erro.
                    return request.render('fgmed_auth_users.template_email_not_found', {
                        'error': "O e-mail fornecido não está associado a uma conta habilitada para redefinição de senha."
                    })
                elif user:
                    reset_token = secrets.token_urlsafe(32)  # Gera um token seguro
                    expiration_time = datetime.now() + timedelta(minutes=20)
                    user.sudo().write({
                        'reset_password_token': reset_token,
                        'reset_password_token_expiration': expiration_time,
                    })
                    # Enviar o e-mail com o link para redefinição de senha
                    reset_url = werkzeug.urls.url_join(request.httprequest.url_root, 'update_password?token=%s' % reset_token)
                    template = request.env.ref('fgmed_auth_users.email_template_reset_password')
                    if template:
                        request.env['mail.template'].browse(template.id).sudo().with_context(reset_url=reset_url).send_mail(user.id, force_send=True)
                    return request.render('fgmed_auth_users.template_reset_password_sent')
                else:
                    return request.render('fgmed_auth_users.template_email_not_found', {
                        'error': "Nenhum usuário encontrado com o endereço de e-mail fornecido."
                    })
            else:
                return request.render('fgmed_auth_users.template_email_not_found', {
                    'error': "Nenhum contato encontrado com o endereço de e-mail fornecido."
                })
        else:
            request.render('fgmed_auth_users.template_reset_password_form', {
            'error': 'Por favor, insira um endereço de e-mail válido.'
            })
            return Response(json.dumps({'error': 'E-mail não encontrado.'}), status=400, content_type='application/json') 

    @http.route(['/update_password'], type='http', auth='public', website=True, csrf=True)
    def update_password(self, **post):
        # Obter o token de redefinição de senha do parâmetro da URL (GET) ou do corpo da solicitação (POST)
        token = request.params.get('token') if request.httprequest.method == 'GET' else post.get('token')

        if request.httprequest.method == 'GET':
            # Renderizar o template com o formulário para o usuário inserir a nova senha
            return request.render('fgmed_auth_users.template_reset_password', {'token': token})

        elif request.httprequest.method == 'POST':
            user = request.env['custom.auth.user'].sudo().search([
                ('reset_password_token', '=', token),
                ('reset_password_token_expiration', '>', fields.Datetime.now())
            ], limit=1)

            if not user:
                # Token inválido ou expirado
                return request.render('fgmed_auth_users.template_reset_password_expired', {'token': token})

            password = post.get('password')
            confirm_password = post.get('confirm_password')

            if not password or password != confirm_password:
                # Senhas não coincidem, pedir para o usuário digitar novamente
                return request.render('fgmed_auth_users.template_reset_password', {
                    'error': 'As senhas não coincidem.',
                    'token': token
                })

            # Atualizar a senha no banco de dados
            user.sudo().write({'password': password})
            user.reset_password_token = False
            user.reset_password_token_expiration = False

            # Redirecionar para uma página de confirmação
            return request.render('fgmed_auth_users.template_password_updated')