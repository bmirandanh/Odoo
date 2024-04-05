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
    nota = fields.Float(string='Nota', default=lambda self: self._get_default_nota(), tracking=True)
    status = fields.Selection([('aprovado', 'Aprovado'),('cursando', 'Cursando'), ('reprovado', 'Reprovado'), ('aproveitamento', 'Aproveitamento'), ('aproveitamento (reprovado)', 'Não Aproveitado'), ('Em Aguardo', 'Em Aguardo')], string='Status', compute='_compute_status', store=True, tracking=True)
    allowed_disciplinas = fields.Many2many('informa.disciplina', compute='_compute_allowed_disciplinas', tracking=True)
    sequencia_disciplina = fields.Integer(string='Sequência', compute='_compute_sequencia_disciplina', tracking=True)
    todas_notas_dadas = fields.Boolean(string='Todas Notas Dadas', compute='_compute_todas_notas_dadas', tracking=True)
    allow_grade_editing = fields.Boolean(related='matricula_id.allow_grade_editing', readonly=True)
    formato_nota = fields.Selection([
    ('normal', '0-10'),
    ('porcentagem', '0-100 (%)')
    ], string='Formato da Nota', default='normal', tracking=True)
    numero_matricula = fields.Char(related='matricula_id.numero_matricula', string='Número da Matrícula', readonly=True, store=True, tracking=True)
    
    def action_open_menu(self):
        view_id2 = self.env.ref('modelo_de_cursos_e_matricula.view_course_management_form').id
        return {
            'name': 'Menu Principal',
            'type': 'ir.actions.act_window',
            'res_model': 'course.creation.wizard',
            'view_mode': 'form',
            'view_id': view_id2,
            'target': 'new',
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'}
        }
    
    def _get_default_nota(self):
        # Retorna None ou False para tentar ter um valor vazio
        return None
        
    def update_grade_from_moodle(self):
        for record in self:
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

            # Verifica se o aluno tem um grade_item com "-" como nota no Moodle antes de prosseguir
            if self.has_no_grade_as_dash(moodle_course_id, moodle_user_id):
                _logger.info('Aluno com ID: %s está cursando a disciplina com ID: %s no Moodle. Configurando status para "cursando".', record.aluno_id.id, record.disciplina_id.id)
                record.write({'status': 'cursando'})
                continue  # Não atualize a nota se o aluno está cursando a disciplina

            grades = self.get_grades_from_moodle(moodle_user_id)
            for grade in grades:
                if str(grade.get("courseid")) == str(moodle_course_id):
                    _logger.info('Encontrada correspondência para courseid: %s', moodle_course_id)
                    grade_str = grade.get("grade")
                    if grade_str and grade_str != '-':
                        try:
                            record.nota = float(grade_str.replace(",", "."))
                            # Após atualizar a nota, recalcular o status com base na nova nota
                            record._compute_status()
                        except ValueError:
                            _logger.error('Valor de nota inválido: %s', grade_str)
                    break
                
    def has_no_grade_as_dash(self, course_id, user_id):
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor            
        
        url = base_url+"webservice/rest/server.php"
        params = {
            "wstoken": token,
            "wsfunction": "gradereport_user_get_grade_items",
            "courseid": course_id,
            "userid": user_id,
            "moodlewsrestformat": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()

        if 'usergrades' in data:
            for grade_item in data['usergrades'][0]['gradeitems']:
                if grade_item['gradeformatted'] == "-":
                    return True
        return False   

    def get_moodle_course_id_int(self, course_id_value): 
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor        
        
        url = base_url+"webservice/rest/server.php"
        
        if course_id_value is None:
            _logger.error('ID do curso não fornecido')
            return None
        
        _logger.info('ID do curso: %s', course_id_value)
        
        params = {
            "wstoken": token,
            "wsfunction": "core_course_get_courses_by_field",
            "field": "idnumber",
            "value": course_id_value,
            "moodlewsrestformat": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()  
        _logger.info('Resposta no Moodle: %s', response.text)
        
        params = {
            "wstoken": token,
            "wsfunction": "core_course_get_courses_by_field",
            "field": "idnumber",
            "value": int(course_id_value),  # Converte o valor para inteiro
            "moodlewsrestformat": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()  
        _logger.info('Resposta no Moodle: %s', response.text)

        if 'courses' in data and len(data['courses']) > 0:
            return data['courses'][0]['id']
        else:
            return None 
           
    def action_update_all_grades_from_moodle(self):
        for record in self:
            record.update_grade_from_moodle()
                    
    def update_all_students_grades_from_moodle(self):
        all_records = self.search([])  # isso buscará todos os registros do modelo 'informa.registro_disciplina'
        for record in all_records:
            curso_id = self.curso_id.id
            aluno_id = self.aluno_id.id
            moodle_curso_id = self.get_moodle_course_id_int(curso_id)
            moodle_aluno_id = self.get_moodle_user_id(aluno_id)
            if moodle_curso_id and moodle_aluno_id and not self.has_no_grade_as_dash(moodle_curso_id, moodle_aluno_id):
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
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor                
        
        url = base_url+"webservice/rest/server.php"
        
        # Extrair o valor inteiro de d_data
        course_id_value = d_data.id
        if course_id_value is None:
            _logger.error('ID não encontrado em d_data: %s', d_data)
            return None
        
        _logger.info('ID: %s', course_id_value)
        
        params = {
            "wstoken": token,
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
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor           
        
        url = base_url+"webservice/rest/server.php"
        _logger.info('user_id: %s', user_id)
        params = {
            "wstoken": token,
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
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor           
        
        url = base_url+"webservice/rest/server.php"
        params = {
            "wstoken": token,
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
            current_group = self.env['informa.curriculo.variant'].search([('sequence', '=', matricula.variant_curriculo_id.current_sequence)], limit=1)

            # Se não encontrou um grupo ou já liberou todas as sequências, retorne
            if not current_group:
                continue

            # Se não tiver uma data de início ou o número de dias desde a data de início for maior ou igual a days_to_release, avance para o próximo grupo
            if not matricula.inscricao_ava or (date.today() - matricula.inscricao_ava).days >= current_group.days_to_release:
                matricula.variant_curriculo_id.last_release_date = date.today()
                matricula.variant_curriculo_id.current_sequence += 1
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
        self.env['audit.log.report'].create_log(record, values, action='create')
        return record

    def write(self, values):
        # Capturar os valores antigos antes da atualização para todos os registros afetados
        old_values = {record.id: {field: getattr(record, field) for field in values} for record in self}

        # Realizar a operação de escrita padrão para atualizar o registro de disciplina
        result = super(RegistroDisciplina, self).write(values)

        # Se 'nota' está entre os valores a serem atualizados
        if 'nota' in values:
            for record in self:
                # Se houver disciplinas sobrepostas
                if record.matricula_id.overlapping_disciplines_ids and record.disciplina_id.id not in record.matricula_id.overlapping_disciplines_ids.ids:
                    continue

                # Verifica se a matrícula associada está com o status 'FINALIZADO'
                if record.matricula_id.status_do_certificado == 'FINALIZADO':
                    raise UserError("Não é possível atualizar a nota para matrículas com status 'FINALIZADO'.")

                # Construa o line_ref para identificar a linha de matrícula correspondente
                line_ref = f'{record.matricula_id.numero_matricula}/{record.disciplina_id.cod_disciplina}'

                # Encontre e atualize a linha de matrícula correspondente
                matricula_lines = self.env['informa.matricula.line'].search([('line_ref', '=', line_ref)])
                for matricula_line in matricula_lines:
                    matricula_line.nota = values['nota']

        # Atualiza o status da matrícula associada, se necessário
        for record in self:
            status_antigo = old_values[record.id].get('status', record.status)
            if 'status' in values and values['status'] != 'aprovado' and status_antigo == 'aprovado':
                # Seu código para atualização no Moodle
                moodle_curso_id = self.env['informa.matricula'].get_moodle_course_id(record.curso_id.id)
                moodle_aluno_id = self.env['informa.matricula'].get_moodle_user_id(record.aluno_id.id)
                if moodle_curso_id and moodle_aluno_id:
                    # Re-inscrever o aluno no curso no Moodle
                    self.env['informa.matricula'].enrol_user_to_course(moodle_aluno_id, moodle_curso_id)

        # Registrar as alterações na auditoria para cada registro
        for record in self:
            changed_values = {k: v for k, v in values.items() if old_values[record.id].get(k) != v}
            if changed_values:
                self.env['audit.log.report'].create_log(record, changed_values, action='write')

        return result

    def unlink(self):
        # Preparar dados para o log de auditoria antes da exclusão
        for record in self:
            log_vals = {
                'model_name': record._name,
                'action': 'unlink',
                'field_name': '',
                'old_value': '',
                'new_value': f'Registro Excluído com ID {record.id}',
                'user_id': self.env.user.id,
                'change_date': fields.Datetime.now(),
            }
            self.env['audit.log.report'].create(log_vals)

        # Chamar o método original de 'unlink'
        return super(RegistroDisciplina, self).unlink()
    
    @api.depends('nota', 'disciplina_media', 'matricula_id.overlapping_disciplines_ids', 'matricula_id.allow_grade_editing')
    def _compute_status(self):
        for record in self:

            # Primeiro, verifica se a nota está vazia
            if record.nota == 0.00:
                record.status = 'Em Aguardo'
                continue  # Vai para a próxima iteração do loop

            # Verificação de allow_grade_editing
            if not record.matricula_id.allow_grade_editing:
                if record.matricula_id.overlapping_disciplines_ids and record.disciplina_id in record.matricula_id.overlapping_disciplines_ids:
                    if record.nota >= record.disciplina_media:
                        record.status = 'aproveitamento'
                    else:
                        record.status = 'aproveitamento (reprovado)'
                    continue

            # Método padrão para calcular o status
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
                grupo = self.env['informa.curriculo.variant'].search([
                    ('disciplina_ids', 'in', [record.disciplina_id.id]),
                    ('id', 'in', record.curso_id.variant_curriculo_id.ids)
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
            current_group = record.curso_id.variant_curriculo_id.filtered(lambda g: g.sequence == allowed_sequence)
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
        
        return record.curso_id.variant_curriculo_id.filtered(lambda g: g.sequence == allowed_sequence).disciplina_ids

    # Retorna a sequência da disciplina para um determinado registro
    def _get_sequencia_disciplina(self, record):
        grupo = self.env['informa.curriculo.variant'].search([('disciplina_ids', 'in', [record.disciplina_id.id])], limit=1)
        return grupo.sequence if grupo else 0
    