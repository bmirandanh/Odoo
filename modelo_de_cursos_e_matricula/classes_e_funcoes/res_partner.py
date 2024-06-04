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

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    aluno = fields.Boolean(string="Aluno ?", default=False, tracking=True)
    professor = fields.Boolean(string="Professor ?", default=False, tracking=True)
    matricula_aluno = fields.Char(string="Registro de aluno", readonly=True, tracking=True)
    cod_professor = fields.Char(string="Registro do professor", readonly=True, tracking=True)
    curso_id = fields.Many2one('informa.cursos', string='Curso Atual', tracking=True)
    matriculas_ids = fields.One2many('informa.matricula', 'nome_do_aluno', string="Matrículas do Aluno", tracking=True)
    
    @api.onchange('professor')
    def _onchange_professor(self):
        # Se 'matricula_aluno' já tiver um valor, não permitimos a modificação
        if self.cod_professor:
            return
        
        # Se o campo 'aluno' é marcado e 'matricula_aluno' não tem valor, geramos um número de matrícula
        if self.professor:
            self.cod_professor = self._generate_unique_matricula_professor()

    def _generate_unique_matricula_professor(self):
        while True:
            cod = self._generate_matricula_professor()
            # Busca no banco de dados para verificar se a matrícula já existe
            existing_partner = self.env['res.partner'].search([('cod_professor', '=', cod)], limit=1)
            
            # Se a matrícula não existir, retorna o valor
            if not existing_partner:
                return cod

    def _generate_matricula_professor(self):
        current_year = fields.Date.today().year
        # Determinar o semestre baseado no mês atual
        faculdade = "FG"
        # Gerar os últimos 4 dígitos aleatoriamente
        last_digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        return f"{faculdade}{current_year}{last_digits}"
    
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
        # Gerar os últimos 4 dígitos aleatoriamente
        last_digits = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        return f"{current_year}{semester}{last_digits}"
    
    @api.model
    def create(self, values):
        # Chamar o método original de 'create'
        record = super(ResPartner, self).create(values)
        # Log de auditoria
        self.env['audit.log.report'].create_log(record, values, action='create')
        return record

    def write(self, values):
        # Log de auditoria antes da alteração
        for rec in self:
            self.env['audit.log.report'].create_log(rec, values, action='write')
        # Chamar o método original de 'write'
        return super(ResPartner, self).write(values)

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
        return super(ResPartner, self).unlink()
    