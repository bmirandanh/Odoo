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

class RegistroDisciplina(models.Model):
    _name = 'informa.registro_disciplina'
    _description = 'Registro de Disciplina do Aluno'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    aluno_id = fields.Many2one('res.partner', string='Aluno', readonly=True, domain=[('is_student', '=', True)], tracking=True)
    curso_id = fields.Many2one('informa.cursos', readonly=True,  string="Curso Relacionado", tracking=True)
    matricula_id = fields.Many2one('informa.matricula', string='Matricula', tracking=True)
    disciplina_id = fields.Many2one('informa.disciplina', string='Disciplina', tracking=True)
    disciplina_media = fields.Float(compute='_compute_disciplina_media', string='Média da Disciplina', tracking=True)
    nota = fields.Float(string='Nota', tracking=True)
    status = fields.Selection([('aprovado', 'Aprovado'), ('reprovado', 'Reprovado'), ('aproveitamento (aprovado)', 'Aproveitamento (Aprovado)'), ('aproveitamento (reprovado)', 'Aproveitamento (Reprovado)')], string='Status', compute='_compute_status', store=True, tracking=True)
    allowed_disciplinas = fields.Many2many('informa.disciplina', compute='_compute_allowed_disciplinas', tracking=True)
    sequencia_disciplina = fields.Integer(string='Sequência', compute='_compute_sequencia_disciplina', tracking=True)
    todas_notas_dadas = fields.Boolean(string='Todas Notas Dadas', compute='_compute_todas_notas_dadas', tracking=True)
    allow_grade_editing = fields.Boolean(related='matricula_id.allow_grade_editing', readonly=True)
    formato_nota = fields.Selection([
    ('normal', '0-10'),
    ('porcentagem', '0-100 (%)')
    ], string='Formato da Nota', default='normal', tracking=True)
        
    def update_grade_from_moodle(self):
        for record in self:
            # Verifique se a matrícula relacionada permite edição de notas para disciplinas sobrepostas.
            if record.matricula_id.allow_grade_editing:
                overlapping_disciplines = record.matricula_id.overlapping_disciplines_ids.ids
                if record.disciplina_id.id in overlapping_disciplines:
                    _logger.info('Disciplina sobreposta com edição de nota permitida na matrícula; ignorando a atualização automática de notas para a disciplina com ID: %s', record.disciplina_id.id)
                    continue  # Pula a atualização desta nota

            moodle_user_id = self.get_moodle_user_id(record.aluno_id.id)
            if moodle_user_id is None:
                _logger.warning('Moodle user_id não encontrado para o aluno com ID: %s', record.aluno_id.id)
                continue

            moodle_course_id = self.get_moodle_course_id(record.disciplina_id)
            if moodle_course_id is None:
                _logger.warning('Moodle course_id não encontrado para a disciplina com ID: %s', record.disciplina_id.id)
                continue

            grades = self.get_grades_from_moodle(moodle_user_id)
            for grade in grades:
                if str(grade.get("courseid")) == str(moodle_course_id):
                    _logger.info('Encontrada correspondência para courseid: %s', moodle_course_id)
                    grade_str = grade.get("grade")
                    _logger.info('Encontrada correspondência para grade_str: %s', grade_str)
                    if grade_str and grade_str != '-':
                        try:
                            record.nota = float(grade_str.replace(",", "."))
                        except ValueError:
                            _logger.error('Valor de nota inválido: %s', grade_str)
                    else:
                        record.nota = 6.0
                        _logger.info('Nota padrão atribuída para grade_str vazio ou "-": %s', grade_str)
                    break
    
    def action_update_all_grades_from_moodle(self):
        for record in self:
            record.update_grade_from_moodle()
    
    def update_all_students_grades_from_moodle(self):
        all_records = self.search([])  # isso buscará todos os registros do modelo 'informa.registro_disciplina'
        for record in all_records:
            record.update_grade_from_moodle()

    def action_open_form_view(self):
        self.ensure_one()
        return {
            'name': 'Detalhes de Disciplina',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.registro_disciplina',
            'view_mode': 'form',
            'view_id': self.env.ref('modelo_de_cursos_e_matricula.view_registro_disciplina_form').id,
            'res_id': self.id,
        }            
    
    def get_moodle_course_id(self, d_data):
        url = "https://avadev.medflix.club/webservice/rest/server.php"
        
        # Extrair o valor inteiro de d_data
        course_id_value = d_data.id
        if course_id_value is None:
            _logger.error('ID não encontrado em d_data: %s', d_data)
            return None
        
        _logger.info('ID: %s', course_id_value)
        
        params = {
            "wstoken": "c502156af2c00a4b3e9e5d878922be46",
            "wsfunction": "core_course_get_courses_by_field",
            "field": "idnumber",
            "value": int(course_id_value),  # Converte o valor para inteiro
            "moodlewsrestformat": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()  
        _logger.info('get_moodle_course_id - course_id_value - Resposta: %s', course_id_value)
        _logger.info('get_moodle_course_id - Resposta no Moodle: %s', response.text)

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
        _logger.info('get_moodle_user_id - user_id - Resposta: %s', user_id)
        _logger.info('get_moodle_user_id - Resposta no Moodle: %s', response.text)
        
        if data and len(data) > 0:
            return data[0]['id']
        else:
            return None
        
    def get_grades_from_moodle(self, moodle_user_id):
        url = "https://avadev.medflix.club/webservice/rest/server.php"
        params = {
            "wstoken": "c502156af2c00a4b3e9e5d878922be46",
            "wsfunction": "gradereport_overview_get_course_grades",
            "moodlewsrestformat": "json",
            "userid": moodle_user_id
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Isso vai lançar um erro para respostas HTTP 4xx/5xx
            data = response.json()
            _logger.info('Resposta completa do Moodle: %s', data)
            return data.get("grades", [])
        except requests.exceptions.HTTPError as errh:
            _logger.error('Erro HTTP: %s', errh)
        except requests.exceptions.ConnectionError as errc:
            _logger.error('Erro de Conexão: %s', errc)
        except requests.exceptions.Timeout as errt:
            _logger.error('Timeout: %s', errt)
        except requests.exceptions.RequestException as err:
            _logger.error('Erro na Requisição: %s', err)
        return []  # Retorne uma lista vazia em caso de erro



    @api.model
    def auto_release_disciplines(self):
        current_sequence = self.current_sequence
        # Pegue todas as matrículas que estão cursando
        matriculas = self.search([('status_do_certificado', '=', 'CURSANDO')])

        for matricula in matriculas:
            # A lógica de liberação das disciplinas será semelhante à nossa função anterior
            current_group = self.env['informa.grupo_disciplina'].search([('sequence', '=', matricula.grupo_disciplina_id.current_sequence)], limit=1)

            # Se não encontrou um grupo ou já liberou todas as sequências, retorne
            if not current_group:
                continue

            # Se não tiver uma data de início ou o número de dias desde a data de início for maior ou igual a days_to_release, avance para o próximo grupo
            if not matricula.inscricao_ava or (date.today() - matricula.inscricao_ava).days >= current_group.days_to_release:
                matricula.grupo_disciplina_id.last_release_date = date.today()
                matricula.grupo_disciplina_id.current_sequence += 1
                # Aqui, você pode adicionar as disciplinas liberadas para o estudante
                matricula.disciplina_ids |= current_group.disciplina_ids
    
    def _validate_nota(self, nota):
        for record in self:
            formato_nota_curso = record.curso_id.formato_nota
            if formato_nota_curso == 'normal' and not (0 <= nota <= 10):
                raise ValidationError(_("A nota deve estar entre 0 e 10."))
            elif formato_nota_curso == 'porcentagem' and not (0 <= nota <= 100):
                raise ValidationError(_("A nota em porcentagem deve estar entre 0 e 100."))
    
    @api.onchange('curso_id', 'aluno_id')
    def _onchange_curso_or_aluno(self):
        if self.curso_id and self.aluno_id:
            allowed_disciplinas = self._get_allowed_disciplinas(self)
            return {'domain': {'disciplina_id': [('id', 'in', allowed_disciplinas.ids)]}}
        return {'domain': {'disciplina_id': []}}

    @api.depends('nota')
    def _compute_todas_notas_dadas(self):
        for record in self:
            # Verifique se todas as notas foram fornecidas. 
            # Você pode ajustar essa lógica conforme necessário.
            record.todas_notas_dadas = bool(record.nota)

    @api.depends('disciplina_id.media', 'curso_id.formato_nota')
    def _compute_disciplina_media(self):
        for record in self:
            formato_nota_curso = record.curso_id.formato_nota
            if formato_nota_curso == 'normal':
                record.disciplina_media = record.disciplina_id.media
            elif formato_nota_curso == 'porcentagem':
                record.disciplina_media = record.disciplina_id.media * 10
    
    @api.model
    def create(self, values):
        record = super(RegistroDisciplina, self).create(values)
        # Se 'nota' está entre os valores a serem atualizados e 'allow_grade_editing' é verdadeiro
        if 'nota' in values:
            for record in self:
                # Se houver disciplinas sobrepostas e a edição da nota é permitida
                if record.matricula_id.overlapping_disciplines_ids:
                    # Verifica se a disciplina atual está na lista de disciplinas sobrepostas
                    if record.disciplina_id.id not in record.matricula_id.overlapping_disciplines_ids.ids:
                        continue
        # Se um novo registro de disciplina for criado, atualize o status da matrícula associada
        if record.matricula_id:
            record.matricula_id.atualizar_status_matricula()
        return record

    def write(self, values):
        result = super(RegistroDisciplina, self).write(values)
        # Se 'nota' está entre os valores a serem atualizados e 'allow_grade_editing' é verdadeiro
        if 'nota' in values:
            for record in self:
                # Se houver disciplinas sobrepostas e a edição da nota é permitida
                if record.matricula_id.overlapping_disciplines_ids:
                    # Verifica se a disciplina atual está na lista de disciplinas sobrepostas
                    if record.disciplina_id.id not in record.matricula_id.overlapping_disciplines_ids.ids:
                        continue
    
        # Se o registro de disciplina for atualizado, atualize o status da matrícula associada
        for record in self:
            if record.matricula_id:
                record.matricula_id.atualizar_status_matricula()
        return result
    
    @api.depends('nota', 'disciplina_media', 'matricula_id.overlapping_disciplines_ids', 'matricula_id.allow_grade_editing')
    def _compute_status(self):
        for record in self:
            # Verifique se o campo allow_grade_editing está marcado na matrícula relacionada
            if not record.matricula_id.allow_grade_editing:
                # Se allow_grade_editing NÃO está marcado, então verifica se a disciplina está na lista de sobrepostas.
                if record.matricula_id.overlapping_disciplines_ids and record.disciplina_id in record.matricula_id.overlapping_disciplines_ids:
                    # Decida entre Aproveitamento (Aprovado) ou Aproveitamento (Reprovado) baseado na nota e na média.
                    if record.nota >= record.disciplina_media:
                        record.status = 'aproveitamento (aprovado)'
                    else:
                        record.status = 'aproveitamento (reprovado)'
                    continue  # Vai para a próxima iteração do loop, sem executar o código abaixo.

            # Se allow_grade_editing está marcado ou se a disciplina não está na lista de sobrepostas, usa o método padrão.
            record.status = self._get_student_status(record.nota, record.disciplina_media)

    def _get_student_status(self, nota, media):
        # Como essa função é chamada para cada registro, não é necessário iterar novamente sobre `self`.
        formato_nota_curso = self.curso_id.formato_nota
        if formato_nota_curso == 'normal':
            return 'aprovado' if nota >= media else 'reprovado'
        elif formato_nota_curso == 'porcentagem':
            media_percent = media
            return 'aprovado' if nota >= media_percent else 'reprovado'

    @api.depends('curso_id')
    def _compute_allowed_disciplinas(self):
        for record in self:
            record.allowed_disciplinas = self._get_allowed_disciplinas(record)

    @api.depends('curso_id', 'disciplina_id')
    def _compute_sequencia_disciplina(self):
        for record in self:
            if record.curso_id and record.disciplina_id:
                # Procura pelo grupo de disciplinas que contém esta disciplina e está associado ao curso especificado
                grupo = self.env['informa.grupo_disciplina'].search([
                    ('disciplina_ids', 'in', [record.disciplina_id.id]),
                    ('id', 'in', record.curso_id.grupo_disciplina_id.ids)
                ], limit=1)
                
                # Use a sequência desse grupo
                if grupo:
                    record.sequencia_disciplina = grupo.sequence
                else:
                    record.sequencia_disciplina = 0
            else:
                record.sequencia_disciplina = 0

    @api.constrains('nota')
    def _check_nota(self):
        for record in self:
            self._validate_nota(record.nota)

    def _get_allowed_disciplinas(self, record):
        allowed_sequence = 1
        while True:
            current_group = record.curso_id.grupo_disciplina_id.filtered(lambda g: g.sequence == allowed_sequence)
            if not current_group:
                break
            
            approved_disciplines = self.search([
                ('aluno_id', '=', record.aluno_id.id),
                '|', ('status', '=', 'aprovado'), ('status', '=', 'aproveitamento (aprovado)'),
                ('disciplina_id', 'in', current_group.disciplina_ids.ids)
            ])
            
            if len(approved_disciplines) == len(current_group.disciplina_ids):
                allowed_sequence += 1
            else:
                break
        
        return record.curso_id.grupo_disciplina_id.filtered(lambda g: g.sequence == allowed_sequence).disciplina_ids

    # Retorna a sequência da disciplina para um determinado registro
    def _get_sequencia_disciplina(self, record):
        grupo = self.env['informa.grupo_disciplina'].search([('disciplina_ids', 'in', [record.disciplina_id.id])], limit=1)
        return grupo.sequence if grupo else 0
    