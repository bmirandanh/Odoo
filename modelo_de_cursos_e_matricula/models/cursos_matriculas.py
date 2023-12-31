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
        
        
class InformaCursos(models.Model):
    _name = 'informa.cursos'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Cursos'

    name = fields.Char(string='Nome do curso',  required=True, tracking=True, domain=[('aluno', '=', True)])
    status_do_certificado = fields.Selection(related='matricula_id.status_do_certificado', readonly=True)
    numero_matricula = fields.Char(related='matricula_id.numero_matricula', readonly=True)
    matricula_id = fields.One2many('informa.matricula', 'curso', string="Matrículas", readonly=True)
    cod_curso = fields.Char(string='Código do Curso', tracking=True)
    grupo_disciplina_id = fields.Many2many('informa.grupo_disciplina', string='Grupo de Disciplina')
    disciplina_ids = fields.Many2many('informa.disciplina', string='Disciplinas')
    tempo_de_conclusao = fields.Selection([('03M/90D', '03M/90D'), ('06M', '06M'), ('12M', '12M'), ('24M', '24M'), ('36M', '36M'), ('48M', '48M')], string="Tempo de conclusão", required=True, tracking=True)
    formato_nota = fields.Selection([
    ('normal', '0-10'),
    ('porcentagem', '0-100 (%)')
    ], string='Formato da Nota', default='normal', tracking=True, required=True)
    
    @api.constrains('grupo_disciplina_id')
    def _check_duplicate_disciplinas(self):
        for record in self:
            all_disciplinas = self.env['informa.disciplina']
            for grupo in record.grupo_disciplina_id:
                for disciplina in grupo.disciplina_ids:
                    if disciplina in all_disciplinas:
                        raise ValidationError(_("A disciplina '%s' está duplicada em diferentes grupos de disciplinas para o curso '%s'.") % (disciplina.name, record.name))
                    all_disciplinas += disciplina
                    
    @api.constrains('grupo_disciplina_id')
    def _check_sequence_order(self):
        for record in self:
            # Busca as sequências dos grupos de disciplina relacionados ao curso
            sequences = sorted(record.grupo_disciplina_id.mapped('sequence'))

            # Verifica se as sequências estão em ordem contínua
            for index, seq in enumerate(sequences):
                if index != seq:
                    raise ValidationError(_("Os grupos de disciplinas devem ser adicionados em ordem sequencial. Por favor, siga a sequência corretamente."))
    
    def action_open_courses(self):
        # Buscar o registro pelo nome
        curso = self.env['informa.cursos'].search([('name', '=', self.name)], limit=1)
        
        # Se o registro foi encontrado
        if curso:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Detalhes do Curso',
                'res_model': 'informa.cursos',
                'view_mode': 'form',
                'res_id': curso.id,   # ID do registro encontrado
                'target': 'current',
            }
        else:
            # Opcional: Você pode retornar um aviso se o registro não for encontrado.
            return {
                'warning': {
                    'title': "Aviso",
                    'message': "Curso não encontrado!"
                }
            }

class GrupoDisciplina(models.Model):
    _name = 'informa.grupo_disciplina'
    _description = 'Grupo de Disciplinas'
    _order = 'sequence'

    name = fields.Char(string='Nome do Grupo: ', required=True)
    sequence = fields.Integer(string='Sequência', help="Determina a ordem de exibição dos grupos.")
    disciplina_ids = fields.Many2many('informa.disciplina', string="Disciplinas")
    cod_grup_disciplina = fields.Char(string='Código único do grupo de disciplina: ', required=True)
    next_release_date = fields.Date(string="Próxima Data de Liberação", compute="_compute_next_release_date", store=True)
    days_to_release = fields.Integer(string="Dias para Liberação", default=7, help="Número de dias para liberar as disciplinas deste grupo.")
    default_days_to_release = fields.Integer(string="Dias para Liberação", default=7, help="Número de dias para liberar as disciplinas do próximo grupo.")
    current_sequence = fields.Integer(string="Sequência Atual", default=0, help="Armazena a sequência do grupo de disciplinas atualmente sendo liberado.")
    
    _sql_constraints = [
        ('cod_grup_disciplina_unique', 'UNIQUE(cod_grup_disciplina)', 'O código do grupo de disciplina deve ser único!')
    ]

    def decrement_days_to_release(self):
        for record in self.search([]):
            if record.days_to_release > 0:
                record.days_to_release -= 1

    def release_next_group(self):
        # Busque o grupo de disciplinas pela sequência atual
        current_group = self.env['informa.grupo_disciplina'].search([('sequence', '=', self.current_sequence)], limit=1)

        # Se não encontrou um grupo ou já liberou todas as sequências, retorne
        if not current_group:
            return []

        # Se a data atual for maior ou igual a next_release_date, avance para o próximo grupo
        if fields.Date.today() >= current_group.next_release_date:
            self.current_sequence += 1
            return current_group

        return []
    
class Disciplina(models.Model):
    _name = 'informa.disciplina'
    _description = 'Disciplina'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Nome da Disciplina', required=True)
    media = fields.Float(string='Média para Aprovação')
    grupo_disciplina_id = fields.Many2one('informa.grupo_disciplina', string='Grupo de Disciplinas')
    cod_disciplina = fields.Char(string='Código único de disciplina: ', required=True)
    
    def _check_cod_disciplina_in_odoo(self, cod_disciplina):
        existing_disciplina = self.env['informa.disciplina'].search([('cod_disciplina', '=', cod_disciplina)], limit=1)
        if existing_disciplina:
            _logger.info(f"A disciplina com código {cod_disciplina} já existe no Odoo com ID {existing_disciplina.id}.")
            return True
        return False

    def _check_name_in_odoo(self, name):
        existing_disciplina = self.env['informa.disciplina'].search([('name', '=', name)], limit=1)
        if existing_disciplina:
            _logger.info(f"Uma disciplina com o nome {name} já existe no Odoo com ID {existing_disciplina.id}.")
            return True
        return False    
    
    @api.constrains('media')
    def _check_media(self):
        for record in self:
            if record.media < 0 or record.media > 10:
                raise ValidationError(_("A média deve estar entre 0 e 10."))
            
    @api.model
    def create(self, vals):
        cod_disciplina = vals.get('cod_disciplina')
        name = vals.get('name')

        if IS_TEST_ENVIRONMENT:
            exists_cod_in_odoo = self._check_cod_disciplina_in_odoo(cod_disciplina)
            exists_name_in_odoo = self._check_name_in_odoo(name)
            
            if exists_cod_in_odoo:
                raise ValidationError(_("Uma disciplina com este código já existe no Odoo."))

            if exists_name_in_odoo:
                raise ValidationError(_("Uma disciplina com este nome já existe no Odoo."))

        else:
            self._connect_moodle()
            exists_cod_in_odoo = self._check_cod_disciplina_in_odoo(cod_disciplina)
            exists_name_in_odoo = self._check_name_in_odoo(name)
            exists_cod_in_moodle = self._check_if_exists_in_moodle(cod_disciplina)
            exists_name_in_moodle = self._check_name_in_moodle(name)
            
            if exists_cod_in_odoo:
                raise ValidationError(_("Uma disciplina com este código já existe no Odoo."))

            if exists_name_in_odoo:
                raise ValidationError(_("Uma disciplina com este nome já existe no Odoo."))

            if exists_cod_in_moodle:
                _logger.info(f"A disciplina com código {cod_disciplina} já existe no Moodle.")
                raise ValidationError(_("Uma disciplina com este código já existe no Moodle."))

            if exists_name_in_moodle:
                _logger.info(f"Uma disciplina com o nome {name} já existe no Moodle.")
                raise ValidationError(_("Uma disciplina com este nome já existe no Moodle."))

        disciplina = super().create(vals)
        
        self._send_to_moodle(disciplina)

        _logger.info(f"Disciplina {name} (código: {cod_disciplina}) criada com sucesso no Odoo com ID {disciplina.id}.")
        
        return disciplina

    def _connect_moodle(self):
        moodle_url = "https://avadev.medflix.club/webservice/rest/server.php"
        moodle_token = "c502156af2c00a4b3e9e5d878922be46"
        moodle = Moodle(moodle_url, moodle_token)
        return moodle

    def _send_to_moodle(self, disciplina):
        if IS_TEST_ENVIRONMENT:
            _logger.info(f"Simulando envio de disciplina {disciplina.name} para Moodle.")
            return

        base_url = "https://avadev.medflix.club/webservice/rest/server.php"
        token = "c502156af2c00a4b3e9e5d878922be46"
        
        # Construindo o endpoint
        params = {
            "wstoken": token,
            "wsfunction": "core_course_create_courses",
            "moodlewsrestformat": "json",
            "courses[0][shortname]": disciplina.cod_disciplina,
            "courses[0][fullname]": disciplina.name,
            "courses[0][idnumber]": disciplina.id,
            "courses[0][categoryid]": 1  # enviar categoryid como 1
        }

        response = requests.post(base_url, params=params)
        
        if response.status_code == 200:
            _logger.info(f"Disciplina {disciplina.name} enviada com sucesso para o Moodle.")
            _logger.info(f"Resposta do Moodle ao criar a Disciplina: {response.text}")
        else:
            _logger.error(f"Erro ao enviar disciplina {disciplina.name} para o Moodle. Resposta: {response.text}")

    def _check_if_exists_in_moodle(self, cod_disciplina):
        moodle = self._connect_moodle()
        # Supondo que o método para buscar cursos seja core_course_get_courses
        courses = moodle('core_course_get_courses')  # Obtém todos os cursos

        # Verifique se o curso com o cod_disciplina específico existe na lista de cursos
        for course in courses:
            if course['shortname'] == cod_disciplina:
                return True

        return False

    def _check_name_in_moodle(self, name):
        moodle = self._connect_moodle()
        courses = moodle('core_course_get_courses')

        for course in courses:
            if course['fullname'] == name:
                return True

        return False
            
            
class RegistroDisciplina(models.Model):
    _name = 'informa.registro_disciplina'
    _description = 'Registro de Disciplina do Aluno'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    aluno_id = fields.Many2one('res.partner', string='Aluno', readonly=True, domain=[('is_student', '=', True)])
    curso_id = fields.Many2one('informa.cursos', readonly=True,  string="Curso Relacionado")
    matricula_id = fields.Many2one('informa.matricula', string='Matricula')
    disciplina_id = fields.Many2one('informa.disciplina', string='Disciplina')
    disciplina_media = fields.Float(compute='_compute_disciplina_media', string='Média da Disciplina')
    nota = fields.Float(string='Nota')
    status = fields.Selection([('aprovado', 'Aprovado'), ('reprovado', 'Reprovado')], string='Status', compute='_compute_status', store=True)
    allowed_disciplinas = fields.Many2many('informa.disciplina', compute='_compute_allowed_disciplinas')
    sequencia_disciplina = fields.Integer(string='Sequência', compute='_compute_sequencia_disciplina')
    todas_notas_dadas = fields.Boolean(string='Todas Notas Dadas', compute='_compute_todas_notas_dadas')
    formato_nota = fields.Selection([
    ('normal', '0-10'),
    ('porcentagem', '0-100 (%)')
    ], string='Formato da Nota', default='normal')
    
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
    def create(self, vals):
        record = super(RegistroDisciplina, self).create(vals)
        # Se um novo registro de disciplina for criado, atualize o status da matrícula associada
        if record.matricula_id:
            record.matricula_id.atualizar_status_matricula()
        return record

    def write(self, vals):
        result = super(RegistroDisciplina, self).write(vals)
        # Se o registro de disciplina for atualizado, atualize o status da matrícula associada
        for record in self:
            if record.matricula_id:
                record.matricula_id.atualizar_status_matricula()
        return result
    
    @api.depends('nota', 'disciplina_media')
    def _compute_status(self):
        for record in self:
            record.status = self._get_student_status(record.nota, record.disciplina_media)

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

    def _get_student_status(self, nota, media):
        return 'aprovado' if nota >= media else 'reprovado'

    def _get_student_status(self, nota, media):
        for record in self:
            formato_nota_curso = record.curso_id.formato_nota
            if formato_nota_curso == 'normal':
                return 'aprovado' if nota >= media else 'reprovado'
            elif formato_nota_curso == 'porcentagem':
                media_percent = media
                return 'aprovado' if nota >= media_percent else 'reprovado'

    # Retorna disciplinas permitidas para um determinado registro
    def _get_allowed_disciplinas(self, record):
        allowed_sequence = 1
        while True:
            current_group = record.curso_id.grupo_disciplina_id.filtered(lambda g: g.sequence == allowed_sequence)
            if not current_group:
                break
            
            approved_disciplines = self.search([
                ('aluno_id', '=', record.aluno_id.id),
                ('status', '=', 'aprovado'),
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
    
class InformaMatricula(models.Model):
    _name = 'informa.matricula'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Matriculas'
    
    status_do_certificado = fields.Selection(
        [('CURSANDO','CURSANDO'),
        ('EM FINALIZAÇÃO','EM FINALIZAÇÃO'),
        ('FINALIZADO','FINALIZADO'),
        ('EM PRAZO EXCEDIDO','EM PRAZO EXCEDIDO'),
        ('EXPEDIDO','EXPEDIDO'),
        ('MATRÍCULA CANCELADA','MATRÍCULA CANCELADA'),
        ],
        compute='_compute_status_certificado', default="CURSANDO", store=True, tracking=True
    )
    regiao = fields.Selection([
        ('AVA','AVA'),
        ('PRESENCIAL','PRESENCIAL'),
        ] , required=True, tracking=True)
    justificativa_cancelamento = fields.Text(string="Justificativa de Cancelamento", tracking=True)
    inscricao_ava = fields.Date(string='Inscrição Ava', required=True, tracking=True)
    email = fields.Char(string="Email", tracking=True)
    telefone = fields.Char(string="Telefone", tracking=True)
    nome_do_aluno = fields.Many2one('res.partner', string="Aluno", required=True, tracking=True, domain=[('aluno', '=', True)])
    curso = fields.Many2one('informa.cursos', string="Curso", required=True, tracking=True)
    prazo_exp_certf_dias = fields.Char(compute='_compute_prazo_exp_certf_dias', string='Prazo exp. Certf. Em dias', tracking=True)
    numero_de_modulo = fields.Char(compute='_compute_numero_de_modulo', tracking=True, string='Nº de Módulo', store=True)
    data_provavel_certificacao = fields.Date(compute='_compute_data_provavel_certificacao', tracking=True, string='Data provável de certificação', store=True)
    tipo_de_ingresso = fields.Many2one('tipo.de.ingresso', string="Tipo de ingresso", required=True, tracking=True)
    tipo_de_cancelamento = fields.Many2one('tipo.de.cancelamento', string="Tipo de Cancelamento", tracking=True)
    color_tipo_ingresso = fields.Integer(related='tipo_de_ingresso.color', string='Color Index from Tipo de Ingresso')
    color_tipo_cancelamento = fields.Integer(related='tipo_de_cancelamento.color', string='Color Index from Tipo de Cancelamento')
    numero_matricula = fields.Char(string="Número de Matrícula", readonly=True)
    matricula_aluno = fields.Char(related='nome_do_aluno.matricula_aluno', string="Matrícula do Aluno", readonly=True)
    cod_curso = fields.Char(compute='_compute_cod_curso', string="Código do Curso", tracking=True, store=True)
    grupo_disciplina_id = fields.Many2one('informa.grupo_disciplina', string='Grupo de Disciplina')
    disciplina_ids = fields.Many2many('informa.disciplina', string='Disciplinas')
    disciplina_nomes = fields.Char(compute='_compute_disciplina_nomes', string='Nome das Disciplinas')
    last_sequence_sent = fields.Integer(string="Sequência já enviada", default=-1, help="Armazena a sequência do grupo de disciplinas que foi enviada por último.")
    current_sequence = fields.Integer(string="Sequência atual", default=0, help="Armazena a sequência do grupo atual de disciplinas.")
    
    def _connect_moodle(self):
        moodle_url = "https://avadev.medflix.club/webservice/rest/server.php"
        moodle_token = "c502156af2c00a4b3e9e5d878922be46"
        moodle = Moodle(moodle_url, moodle_token)
        return moodle
    
    def execute_for_all(self):
        _logger.info('Executando método execute_for_all...')
        matricula = self.env['informa.matricula']
        matriculas = self.env['informa.matricula'].search([
            ('status_do_certificado', 'in', ['CURSANDO', 'EM FINALIZAÇÃO', 'EM PRAZO EXCEDIDO'])
        ])
        for matricula in matriculas:
            self.get_released_groups(matricula.id)
        _logger.info('Método execute_for_all concluído.')
        return True
          
            
    # Quando os valores dos campos de um registro Disciplina são atualizados, esse método é chamado.
    def write(self, vals):
        _logger.info('Atualizando valores do registro InformaMatricula...')
        res = super().write(vals)  # Chamando o método da classe pai corretamente
       # self.update_moodle_information()
        _logger.info('Valores do registro InformaMatricula atualizados.')
        return res
    
    def get_moodle_course_id(self, d_data):
        url = "https://avadev.medflix.club/webservice/rest/server.php"
        
        # Extrair o valor inteiro de d_data
        course_id_value = d_data.get('id')
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
    
    ##### Aqui inicia os métodos de atualização da Cron, em questão a vinculação das disciplinas para os alunos
     
    def enrol_user_to_course(self, user_id, course_id):
        # URL base para o serviço web do Moodle
        MOODLE_URL = "https://avadev.medflix.club/webservice/rest/server.php"
        
        # Parâmetros para a requisição
        params = {
            "wstoken": "c502156af2c00a4b3e9e5d878922be46",
            "wsfunction": "enrol_manual_enrol_users",
            "moodlewsrestformat": "json",
            "enrolments[0][roleid]": 5,
            "enrolments[0][userid]": user_id,
            "enrolments[0][courseid]": course_id
        }
        
        # Fazendo a requisição POST
        response = requests.post(MOODLE_URL, params=params)
            
        if response.status_code == 200:
            _logger.error('Resposta no Moodle: %s', response.text)
            return response.json()
        else:
            _logger.error('Erro ao inscrever usuário no curso no Moodle: %s', response.text)
            raise UserError(_('Erro ao inscrever usuário no curso no Moodle! Houve algum problema na inscrição.'))

    
    def get_released_groups(self, matricula_id):
        matricula = self.env['informa.matricula'].browse(matricula_id)
        _logger.info('Obtendo grupos liberados para a matrícula ID %d...', matricula_id)

        if not matricula:
            return {'error': 'Matrícula não encontrada.'}

        aluno_name = matricula.nome_do_aluno.name
        _logger.info('Matrícula pertence ao aluno %s.', aluno_name)

        curso = matricula.curso
        if not curso:
            return {'error': 'Curso não associado à matrícula.'}

        grupos = curso.grupo_disciplina_id.sorted(key=lambda g: g.sequence)
        current_sequence = matricula.current_sequence
        user_id = matricula.nome_do_aluno.id
        _logger.info('user_id = %s.', user_id)

        # Trata o caso especial da sequência 0
        _logger.info('current_sequence = %s.', matricula.current_sequence)
        if matricula.current_sequence == 0:
            if grupos[current_sequence].days_to_release <= 0:
                disciplinas_data = [{
                    'id': disciplina.id,
                } for disciplina in grupos[current_sequence].disciplina_ids]
                _logger.info('disciplinas_data = %s.', disciplinas_data)
                for d_data in disciplinas_data:
                    moodle_course_id = self.get_moodle_course_id(d_data)
                    _logger.info('d_data = %s', d_data)
                    _logger.info('moodle_course_id = %s', moodle_course_id)
                    moodle_user_id = self.get_moodle_user_id(user_id)
                    _logger.info('moodle_user_id = %s', moodle_user_id)
                    if moodle_course_id and moodle_user_id:
                        _logger.info('Enviando para %s, o id de curso = %s.', moodle_user_id, moodle_course_id)
                        matricula.current_sequence += 1
                        return self.enrol_user_to_course(user_id=moodle_user_id, course_id=moodle_course_id)
                    else:
                        _logger.info('Erro no GET de get_moodle_course_id.') 
            else:
                _logger.info(' Ainda não é tempo de liberar a sequência 0 ')
                

        # Tratando sequências posteriores
        else:
            disciplinas_anteriores = grupos[current_sequence-1].disciplina_ids
            _logger.info('disciplinas_anteriores = %s.', disciplinas_anteriores)
            registros_disciplinas = self.env['informa.registro_disciplina'].search([
                ('matricula_id', '=', matricula.id),
                ('disciplina_id', 'in', disciplinas_anteriores.ids)
            ])
            if all(record.status == 'aprovado' for record in registros_disciplinas):
                if grupos[current_sequence].days_to_release <= 0:
                    disciplinas_data = [{
                        'id': disciplina.id,
                    } for disciplina in grupos[current_sequence].disciplina_ids]
                    _logger.info('disciplinas_data = %s.', disciplinas_data)
                    for d_data in disciplinas_data:
                        moodle_course_id = self.get_moodle_course_id(d_data)
                        _logger.info('moodle_course_id = %s', moodle_course_id)
                        moodle_user_id = self.get_moodle_user_id(user_id)
                        _logger.info('moodle_user_id = %s', moodle_user_id)
                        if moodle_course_id and moodle_user_id:
                            _logger.info('Enviando para %s, o id de curso = %s.', moodle_user_id, moodle_course_id)
                            matricula.last_sequence_sent = matricula.current_sequence
                            matricula.current_sequence += 1
                            _logger.info('current_sequence = %s.', matricula.current_sequence)
                            return self.enrol_user_to_course(user_id=moodle_user_id, course_id=moodle_course_id)
                        else:
                            _logger.info('Erro no GET de get_moodle_course_id.')
                else:
                    _logger.info('Ainda não é tempo de liberar a sequência atual.')
            else:
                _logger.info(' O aluno ainda não passou em todas as disciplinas da sequência anterior.')

        return {'message': 'Cron concluída.'}
        # Fim dos métodos de atualização da Cron para vinculação das disciplinas aos alunos
    
    # métodos de update de informações para o moodle    
    def update_moodle_information(self):
        """
        Envia informações atualizadas da matrícula para o Moodle.
        """
        for matricula in self:
            aluno_name = matricula.nome_do_aluno.name
            curso_name = matricula.curso.name if matricula.curso else ''
            email = matricula.email
            telefone = matricula.telefone
            
            data_to_send = {
                'matricula_id': matricula.id,
                'aluno_name': aluno_name,
                'curso_name': curso_name,
                'email': email,
                'telefone': telefone
            }
            
            if IS_TEST_ENVIRONMENT:
                _logger.info('Envio simulado para o Moodle. Informações da Matrícula: %s', data_to_send)
                return {
                    'message': 'Envio realizado (simulado)',
                    'data': data_to_send
                }

            moodle = self._connect_moodle()
            # O método para atualizar informações da matrícula seja 'custom_method_update_matricula'
            response = moodle('custom_method_update_matricula', data_to_send)
            
            # Suponha que a resposta seja um dicionário e tenha uma chave 'success'
            if not response.get('success'):
                _logger.error('Erro ao enviar dados para o Moodle.')
        return True

    def custom_method_update_matricula(self, data):
        """
        Método para atualizar as informações do aluno no Moodle.

        :param data: Um dicionário contendo as informações do aluno que precisam ser atualizadas.
        :return: Um dicionário contendo informações sobre o sucesso ou falha da operação.
        """
        moodle = self._connect_moodle()

        # Primeiro, tente obter o ID do aluno no Moodle usando o nome (ou outra identificação única, como e-mail ou matrícula).
        try:
            response = moodle.call('core_user_get_users', {'criteria': [{'key': 'username', 'value': data['aluno_name']}]})
            if not response:
                return {'success': False, 'message': "Aluno não encontrado no Moodle."}
            user_id = response[0]['id']
        except Exception as e:
            return {'success': False, 'message': f"Erro ao buscar aluno no Moodle: {e}"}

        # Atualizar as informações do aluno.
        # Presumindo que o Moodle tenha uma função chamada 'core_user_update_users' para atualizar informações do usuário.
        users_data = [{
            'id': user_id,
            'firstname': data.get('firstname', ''),
            'lastname': data.get('lastname', ''),
            'email': data.get('email', ''),
        }]
        try:
            moodle.call('core_user_update_users', users_data)
            return {'success': True, 'message': "Informações do aluno atualizadas com sucesso."}
        except Exception as e:
            return {'success': False, 'message': f"Erro ao atualizar informações do aluno: {e}"}   
    
    def show_student_disciplines(self):
        self.ensure_one()

        domain = [
            ('aluno_id', '=', self.nome_do_aluno.id),
            ('curso_id', '=', self.curso.id)
        ]

        return {
            'name': 'Disciplinas de ' + str(self.nome_do_aluno.name),
            'type': 'ir.actions.act_window',
            'res_model': 'informa.registro_disciplina',
            'view_mode': 'tree',
            'view_id': self.env.ref('modelo_de_cursos_e_matricula.view_registro_disciplina_tree').id,
            'domain': domain,
            'context': {
                'default_aluno_id': self.nome_do_aluno.id,
                'default_curso_id': self.curso.id
            }
        }
        
    def reingressar_matricula_wizard(self):
        self.ensure_one()  # Garante que apenas um registro é selecionado
        view_id = self.env.ref('modelo_de_cursos_e_matricula.view_matricula_reingresso_wizard_form').id
        return {
            'name': 'Re-ingressar Matrícula',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'matricula.reingresso.wizard',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_matricula_id': self.id}
        }
        
    @api.depends('disciplina_ids')
    def _compute_disciplina_nomes(self):
        for record in self:
            names = ", ".join(record.disciplina_ids.mapped('name'))
            record.disciplina_nomes = names
    
    def atualizar_status_matricula(self):
        for matricula in self:
            registros_disciplina = self.env['informa.registro_disciplina'].search([('matricula_id', '=', matricula.id)])
            if all(record.status == 'aprovado' for record in registros_disciplina):
                matricula.status_do_certificado = 'FINALIZADO'
    
    def _update_related_disciplinas(self):
        for matricula in self:
            disciplinas = self.env['informa.registro_disciplina'].search([('matricula_id', '=', matricula.id)]).mapped('disciplina_id')
            matricula.disciplina_ids = [(6, 0, disciplinas.ids)]
    
    @api.model
    def create(self, vals):
        # Primeiro, verifique se o aluno já tem uma matrícula no curso especificado.
        aluno_id = vals.get('nome_do_aluno')
        curso_id = vals.get('curso')
        existing_matricula = self.search([('nome_do_aluno', '=', aluno_id), ('curso', '=', curso_id)])
        
        if existing_matricula:
            raise UserError(_('O aluno já possui uma matrícula neste curso!'))
        
        # Se não houver matrícula existente, crie a nova matrícula.
        matricula_record = super(InformaMatricula, self).create(vals)
        
        # Pegue as disciplinas permitidas para o curso associado à matrícula.
        allowed_disciplinas = self.compute_allowed_disciplinas(matricula_record.curso)
        
        # Para cada disciplina permitida, crie um novo registro de 'RegistroDisciplina'.
        for disciplina in allowed_disciplinas:
            if disciplina.id:
                self.env['informa.registro_disciplina'].create({
                    'aluno_id': matricula_record.nome_do_aluno.id,
                    'curso_id': matricula_record.curso.id,
                    'matricula_id': matricula_record.id,
                    'disciplina_id': disciplina.id,
                })
                
        if not self._context.get('skip_status_update'):
            matricula_record.with_context(skip_status_update=True).atualizar_status_matricula()
            
       # Método para levar as informações para o moodle 
        self._register_student_in_moodle(matricula_record)
        
        return matricula_record

    def write(self, vals):
        result = super(InformaMatricula, self).write(vals)
        
        # Se algum dos campos de interesse foi alterado, envie atualizações para o Moodle
        fields_of_interest = ['email', 'telefone', 'nome_do_aluno', 'curso']

        if any(field in vals for field in fields_of_interest):
            self.update_moodle_information()

        if not self._context.get('skip_status_update'):
            self.with_context(skip_status_update=True).atualizar_status_matricula()

        return result

    def _register_student_in_moodle(self, matricula):
        base_url = "https://avadev.medflix.club/webservice/rest/server.php"
        token = "c502156af2c00a4b3e9e5d878922be46"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Divida o nome completo no primeiro espaço
        names = matricula.nome_do_aluno.name.split(' ', 1)
        firstname = names[0]
        lastname = names[1] if len(names) > 1 else firstname
        cpf = matricula.nome_do_aluno.l10n_br_cnpj_cpf
        cpfform = 'Fg@'+cpf
        matricula_id = matricula.nome_do_aluno.id

        if IS_TEST_ENVIRONMENT:
            # Se estivermos em um ambiente de teste, simplesmente logue a simulação e retorne.
            _logger.info('Envio simulado para o Moodle. Nome do aluno: %s, CPF: %s', matricula.nome_do_aluno.name, cpf)
            return {
                'message': 'Envio realizado (simulado)',
                'data': {
                    "username": cpf,
                    "firstname": firstname,
                    "lastname": lastname,
                    "email": matricula.email
                }
            }

        # Primeiro, verifique se o usuário já existe
        user_check_url = f"{base_url}/webservice/rest/server.php?wstoken={token}&wsfunction=core_user_get_users&moodlewsrestformat=json&criteria[0][key]=username&criteria[0][value]={cpf}"
        response = requests.get(user_check_url, headers=headers)
        users = response.json().get('users', [])

        if not users:
            # Construir os dados para a criação do usuário
            user_data = {
                "users[0][username]": cpf,
                "users[0][password]": cpfform,
                "users[0][firstname]": firstname,
                "users[0][lastname]": lastname,
                "users[0][email]": matricula.email,
                "users[0][idnumber]":matricula_id,
            }
       
        # Se o usuário não existir, criamos um novo
        signup_url = f"{base_url}/webservice/rest/server.php?wstoken={token}&wsfunction=core_user_create_users&moodlewsrestformat=json"
        for key, value in user_data.items():
            signup_url += f"&{key}={value}"

        response = requests.get(signup_url, headers=headers)  # Usamos GET aqui
        _logger.info('Resposta do Moodle ao criar usuário: %s', response.text)
        if response.status_code != 200:
            _logger.error('Erro ao criar usuário no Moodle: %s', response.text)
            raise UserError(_('Erro ao criar usuário no Moodle! O usuário já existe ou houve algum problema na criação.'))
    
    def compute_allowed_disciplinas(self, curso_id):
        # Buscar todas as disciplinas associadas aos grupos de disciplinas do curso selecionado
        disciplinas = self.env['informa.disciplina']
        for grupo in curso_id.grupo_disciplina_id:
            disciplinas |= grupo.disciplina_ids
        return disciplinas
                
    @api.onchange('nome_do_aluno')
    def _onchange_nome_do_aluno(self):
    # Se o campo nome_do_aluno não estiver definido, apenas retorne.
        if not self.nome_do_aluno:
            self.email = False
            self.telefone = False
            return

        # Atualiza os campos email e telefone com os valores do aluno selecionado.
        self.email = self.nome_do_aluno.email
        self.telefone = self.nome_do_aluno.phone
           
    @api.depends('curso')
    def _compute_cod_curso(self):
        for record in self:
            record.cod_curso = record.curso.cod_curso if record.curso else False
    
    @api.onchange('cod_curso', 'nome_do_aluno', 'inscricao_ava')
    def _onchange_cod_curso(self):
        # Se nome_do_aluno, inscricao_ava ou cod_curso não estiverem definidos, apenas retorne.
        if not self.nome_do_aluno or not self.inscricao_ava or not self.cod_curso:
            return
        
        # Caso contrário, atualize numero_matricula.
        self.numero_matricula = self._generate_matricula()

    def _generate_matricula(self):
        # Verifica se cod_curso não está vazio.
        if not self.cod_curso:
            raise UserError('Por favor, preencha o Código do Curso antes de gerar a matrícula.')
        
        # Pegar os 7 últimos dígitos do campo matricula_aluno do aluno selecionado
        last_digits = self.nome_do_aluno.matricula_aluno[-7:] if self.nome_do_aluno.matricula_aluno else ''
        
        if not last_digits or len(last_digits) < 7:
            raise UserError('O campo matricula_aluno do aluno selecionado está incorreto ou não definido.')

        # Combina tudo
        matricula = f"{self.cod_curso}{last_digits}"
        return matricula
    
    @api.depends('numero_de_modulo', 'inscricao_ava')
    def _compute_data_provavel_certificacao(self):
        for record in self:
            if record.inscricao_ava:
                if record.numero_de_modulo == '03M/90D':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=3)
                elif record.numero_de_modulo == '06M':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=6)
                elif record.numero_de_modulo == '12M':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=12)
                elif record.numero_de_modulo == '24M':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=24)
                elif record.numero_de_modulo == '36M':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=36)
                elif record.numero_de_modulo == '48M':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=48)
                else:
                    record.data_provavel_certificacao = False
            else:
                record.data_provavel_certificacao = False

    @api.depends('curso.tempo_de_conclusao')
    def _compute_numero_de_modulo(self):
        for record in self:
            record.numero_de_modulo = record.curso.tempo_de_conclusao or False
            
    @api.depends('status_do_certificado', 'data_provavel_certificacao', 'inscricao_ava')
    def _compute_prazo_exp_certf_dias(self):
        for record in self:
            if record.status_do_certificado == 'EXPEDIDO':
                record.prazo_exp_certf_dias = "Expedido"
            elif record.status_do_certificado == 'MATRÍCULA CANCELADA':
                record.prazo_exp_certf_dias = "Matrícula Cancelada"
            elif record.status_do_certificado == 'FINALIZADO':
                record.prazo_exp_certf_dias = "Curso Finalizado"
            else:
                if record.inscricao_ava and record.data_provavel_certificacao:
                    dias_passados = (record.data_provavel_certificacao - date.today()).days
                    record.prazo_exp_certf_dias = str(dias_passados) + _(" dias")
                    
                    # Alteração do status baseado no valor de dias_passados
                    if dias_passados <= 0:
                        record.status_do_certificado = 'EM PRAZO EXCEDIDO'
                    elif dias_passados <= 10:
                        record.status_do_certificado = 'EM FINALIZAÇÃO'
                    else:
                        record.status_do_certificado = 'CURSANDO'
                else:
                    record.prazo_exp_certf_dias = _("Data de provável certificação não definida")

    
    def atualizar_status_dias_passados(self):
        records = self.search([])
        for record in records:
            record._compute_prazo_exp_certf_dias()


    def action_open_status_change_wizard(self):
        context = {
            'default_matricula_id': self.id,
        }
        return {
            'name': _('Cancelamento da Matrícula'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'matricula.status.change.wizard',
            'target': 'new',
            'context': context,
        }           

class TipoIngresso(models.Model):
    _name = 'tipo.de.ingresso'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Tipo de Ingresso'
    _rec_name = 'nome'
    
    nome = fields.Char(string="nome", required=True, tracking=True)
    descricao = fields.Char(string="descrição", required=True, tracking=True)
    color = fields.Integer(string='Color Index')
    
class TipoCancelamento(models.Model):
    _name = 'tipo.de.cancelamento'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Tipo de Cancelamento'
    _rec_name = 'nome'

    nome = fields.Char(string="nome", required=True, tracking=True)
    descricao = fields.Char(string="descrição", required=True, tracking=True)
    color = fields.Integer(string='Color Index')
    
            
            
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

    def change_status(self):
        if self.matricula_id:

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
                self.matricula_id.data_provavel_certificacao = date.today() + relativedelta(months=48)
                self.matricula_id.prazo_exp_certf_dias = "Matrícula Cancelada"
                # Altera o tipo de cancelamento selecionado para a matrícula
                self.matricula_id.tipo_de_cancelamento = self.tipo_de_cancelamento    
                # Altera o color_tipo_cancelamento pelo color do tipo de cancelamento selecionado
                self.matricula_id.color_tipo_cancelamento = self.tipo_de_cancelamento.color

                    
            # Registra a justificativa como uma mensagem de rastreamento na matrícula
            self.matricula_id.message_post(body=_("Justificativa para alteração de status: %s") % (self.justificativa,))

class MatriculaReingressoWizard(models.Model):
    _name = 'matricula.reingresso.wizard'
    _description = 'Assistente para Re-ingresso de Matrícula'

    matricula_id = fields.Many2one('informa.matricula', string="Matrícula", readonly=True)
    tipo_de_ingresso = fields.Many2one('tipo.de.ingresso', string="Tipo de Ingresso", required=True)
    justificativa = fields.Text(string="Justificativa", required=True)
    data_inscricao = fields.Date(string="Data de Inscrição", required=True, default=fields.Date.today())

    def confirm_reingresso(self):
        if self.matricula_id:
            allowed_statuses = ['MATRÍCULA CANCELADA', 'FINALIZADO', 'EXPEDIDO']
            if self.matricula_id.status_do_certificado not in allowed_statuses:
                raise ValidationError(_("Não é possível realizar re-ingresso com o status '%s'.") % self.matricula_id.status_do_certificado)

            # Zerando notas das disciplinas
            disciplinas = self.env['informa.registro_disciplina'].search([('matricula_id', '=', self.matricula_id.id)])
            for disciplina in disciplinas:
                disciplina.nota = 0.0

            self.matricula_id.message_post(body=_("Justificativa para re-ingresso: %s") % (self.justificativa,))

            self.matricula_id.status_do_certificado = 'CURSANDO'
            self.matricula_id.inscricao_ava = self.data_inscricao
            self.matricula_id.tipo_de_ingresso = self.tipo_de_ingresso

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    aluno = fields.Boolean(string="Aluno ?", default=False) 
    matricula_aluno = fields.Char(string="Matrícula do Aluno", readonly=True)
    curso_id = fields.Many2one('informa.curso', string='Curso Atual')
    matriculas_ids = fields.One2many('informa.matricula', 'nome_do_aluno', string="Matrículas do Aluno")
    
    @api.onchange('aluno')
    def _onchange_aluno(self):
        # Se 'matricula_aluno' já tiver um valor, não permitimos a modificação
        if self.matricula_aluno:
            return
        
        # Se o campo 'aluno' é marcado e 'matricula_aluno' não tem valor, geramos um número de matrícula
        if self.aluno:
            self.matricula_aluno = self._generate_unique_matricula_aluno()

    def _generate_unique_matricula_aluno(self):
        while True:
            matricula = self._generate_matricula_aluno()
            # Busca no banco de dados para verificar se a matrícula já existe
            existing_partner = self.env['res.partner'].search([('matricula_aluno', '=', matricula)], limit=1)
            
            # Se a matrícula não existir, retorna o valor
            if not existing_partner:
                return matricula

    def _generate_matricula_aluno(self):
        current_year = fields.Date.today().year
        # Determinar o semestre baseado no mês atual
        month = fields.Date.today().month
        semester = '01' if month <= 6 else '02'
        # Gerar os últimos 7 dígitos aleatoriamente
        last_digits = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        return f"{current_year}{semester}{last_digits}"
    