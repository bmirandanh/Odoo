from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
import random
from odoo import tools
import logging
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import http
import requests
from moodle import Moodle

IS_TEST_ENVIRONMENT = False
_logger = logging.getLogger(__name__)

class MatriculaStatusChangeWizard(models.Model):
    _name = 'matricula.status.change.wizard'
    _description = 'Assistente para Alteração de Status da Matrícula'

    matricula_id = fields.Many2one('informa.matricula', string="Matrícula", readonly=True)
    new_status = fields.Selection(
        [
            ('MATRÍCULA CANCELADA', 'MATRÍCULA CANCELADA'),
        ], string="Status", required=True)
    tipo_de_cancelamento = fields.Many2one('tipo.de.cancelamento', string="Tipo de Cancelamento")
    justificativa = fields.Text(string="Justificativa", required=True)

    def get_moodle_course_id_int(self, course_id_value): 
        url = "https://avadev.medflix.club/webservice/rest/server.php"
        
        if course_id_value is None:
            _logger.error('ID do curso não fornecido')
            return None
        
        _logger.info('ID do curso: %s', course_id_value)
        
        params = {
            "wstoken": "c502156af2c00a4b3e9e5d878922be46",
            "wsfunction": "core_course_get_courses_by_field",
            "field": "idnumber",
            "value": course_id_value,
            "moodlewsrestformat": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()  
        _logger.info('Resposta no Moodle: %s', response.text)

        if 'courses' in data and len(data['courses']) > 0:
            return data['courses'][0]['id']
        else:
            return None
            
    def get_moodle_user_id(self, user_id):
        url = "https://avadev.medflix.club/webservice/rest/server.php"
        _logger.info('user_id: %s', user_id)
        params = {
            "wstoken": "c502156af2c00a4b3e9e5d878922be46",
            "wsfunction": "core_user_get_users_by_field",
            "field": "idnumber",
            "values[0]": user_id,
            "moodlewsrestformat": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()
        _logger.info('Resposta no Moodle: %s', response.text)
        
        if data and len(data) > 0:
            return data[0]['id']
        else:
            return None
        
    def block_access_to_moodle(self, moodle_aluno_id, moodle_curso_id):
        moodle_url = "https://avadev.medflix.club/webservice/rest/server.php"
        token = "c502156af2c00a4b3e9e5d878922be46"
        user_id = moodle_aluno_id
        course_id = moodle_curso_id
        
        if user_id and course_id:
            params = {
                "wstoken": token,
                "wsfunction": "enrol_manual_unenrol_users",
                "moodlewsrestformat": "json",
                "enrolments[0][userid]": user_id,
                "enrolments[0][courseid]": course_id,
                "enrolments[0][roleid]": 5,
            }
            response = requests.post(moodle_url, params=params)
            if response.status_code == 200:
                _logger.info('Usuário suspenso no Moodle: %s', response.text)
            else:
                _logger.error('Erro ao suspender usuário no Moodle: %s', response.text)
                
    def change_status(self):
        
        if self.matricula_id:
            matricula = self.matricula_id

            # Busca a instância correspondente em 'informa.registro_disciplina'
            registro_disciplina = self.env['informa.registro_disciplina'].search([
                ('curso_id', '=', matricula.curso.id),
                ('aluno_id', '=', matricula.nome_do_aluno.id)
            ], limit=1)

            # Verifica se encontrou a instância
            if not registro_disciplina:
                raise ValidationError(_("Registro de disciplina não encontrado para o aluno da matrícula."))

            # Agora, você pode usar registro_disciplina para obter curso_id e aluno_id
            curso_id = registro_disciplina.curso_id.id
            aluno_id = registro_disciplina.aluno_id.id

            moodle_curso_id = self.get_moodle_course_id_int(curso_id)
            moodle_aluno_id = self.get_moodle_user_id(aluno_id)
               
            # Lista dos status que podem ser cancelados
            allowed_statuses = ['CURSANDO', 'EM FINALIZAÇÃO', 'EM PRAZO EXCEDIDO']

            # Verificar se o status atual está na lista de status permitidos
            if self.matricula_id.status_do_certificado not in allowed_statuses:
                raise ValidationError(_("Não é possível cancelar uma matrícula com status '%s'.") % self.matricula_id.status_do_certificado)

            if self.new_status == 'MATRÍCULA CANCELADA' and not self.tipo_de_cancelamento:
                raise ValidationError(_("Para cancelar a matrícula, é necessário selecionar um tipo de cancelamento."))

            # Altera o status da matrícula
            self.matricula_id.status_do_certificado = self.new_status

            # Se a matrícula for cancelada
            if self.new_status == 'MATRÍCULA CANCELADA':
                self.matricula_id.justificativa_cancelamento = self.justificativa
                self.matricula_id.data_original_certificacao = date.today() + relativedelta(months=48)
                self.matricula_id.prazo_exp_certf_dias = "Matrícula Cancelada"
                # Altera o tipo de cancelamento selecionado para a matrícula
                self.matricula_id.tipo_de_cancelamento = self.tipo_de_cancelamento    
                # Altera o color_tipo_cancelamento pelo color do tipo de cancelamento selecionado
                self.matricula_id.color_tipo_cancelamento = self.tipo_de_cancelamento.color
                self.block_access_to_moodle(moodle_aluno_id, moodle_curso_id)
                    
            # Registra a justificativa como uma mensagem de rastreamento na matrícula
            self.matricula_id.message_post(body=_("Justificativa para alteração de status: %s") % (self.justificativa,))