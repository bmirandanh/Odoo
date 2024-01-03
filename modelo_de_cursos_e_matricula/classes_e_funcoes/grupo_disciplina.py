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

class GrupoDisciplina(models.Model):
    _name = 'informa.grupo_disciplina'
    _description = 'Grupo de Disciplinas'
    _order = 'sequence'

    name = fields.Char(string='Nome do Grupo: ', required=True)
    sequence = fields.Integer(string='Sequência', help="Determina a ordem de exibição dos grupos.")
    disciplina_ids = fields.Many2many('informa.disciplina', string="Disciplinas")
    cod_grup_disciplina = fields.Char(string='Código único do grupo de disciplina: ', required=True)
    next_release_date = fields.Date(string="Próxima Data de Liberação", store=True)
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