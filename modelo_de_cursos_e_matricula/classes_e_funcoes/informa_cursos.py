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
import math

IS_TEST_ENVIRONMENT = False
_logger = logging.getLogger(__name__)

class InformaCursos(models.Model):
    """
    Esta classe representa os cursos disponíveis.
    """    
    _name = 'informa.cursos'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Cursos'

    name = fields.Char(string='Nome do curso', required=True, tracking=True)
    status_do_certificado = fields.Selection(related='matricula_id.status_do_certificado', readonly=True, tracking=True)
    numero_matricula = fields.Char(related='matricula_id.numero_matricula', readonly=True, tracking=True)
    matricula_id = fields.One2many('informa.matricula', 'curso', string="Matrículas", readonly=True, tracking=True)
    cod_curso = fields.Char(string='Código do Curso', tracking=True)
    curriculo_id = fields.Many2one('informa.curriculo', string='Currículo', tracking=True)
    variant_curriculo_id = fields.Many2one('informa.curriculo.variant', string='Versão do Currículo', tracking=True)
    disciplina_ids = fields.Many2many('informa.disciplina', string='Disciplinas', tracking=True)
    formato_nota = fields.Selection([
    ('normal', '0-10'),
    ('porcentagem', '0-100 (%)')
    ], string='Formato da Nota', default='normal', tracking=True, required=True)

    # Campo computado para calcular o tempo de conclusão em meses
    tempo_de_conclusao = fields.Selection(
        string="Tempo de Conclusão Estimado",
        selection=[('03M/90D', '03M/90D'), ('06M', '06M'), ('12M', '12M'), 
                   ('24M', '24M'), ('36M', '36M'), ('48M', '48M')],
        store=True,
    )
    # Vamos considerar que você tem um campo Many2many para variant_curriculo_id
    variant_curriculo_ids = fields.Many2many('informa.curriculo.variant', string='Variantes do Currículo', tracking=True)
    
    # Este campo que é a soma de todas as durações da variante
    total_duracao_horas = fields.Float(
        string='Total de Duração em Horas',
        related='variant_curriculo_id.total_duracao_horas',
        readonly=True,
        tracking=True,
        help="Total de horas da variante do currículo selecionada."
    )
    
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
    
    @api.constrains('variant_curriculo_id')
    def _check_duplicate_disciplinas(self):
        """
        Verifica se há disciplinas duplicadas em diferentes grupos de disciplinas para o curso.
        """        
        for record in self:
            all_disciplinas = self.env['informa.disciplina']
            for grupo in record.variant_curriculo_id:
                for disciplina in grupo.disciplina_ids:
                    if disciplina in all_disciplinas:
                        raise ValidationError(_("A disciplina '%s' está duplicada em diferentes grupos de disciplinas para o curso '%s'.") % (disciplina.name, record.name))
                    all_disciplinas += disciplina
                    
    @api.constrains('variant_curriculo_id')
    def _check_sequence_order(self):
        for record in self:
            # Busca as sequências dos grupos de disciplina relacionados ao curso
            sequences = sorted(record.variant_curriculo_id.mapped('sequence'))

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

    @api.model
    def create(self, values):
        # Chamar o método original de 'create'
        record = super(InformaCursos, self).create(values)

        return record

    def write(self, values):
        
        # Log de auditoria antes da alteração
        for rec in self:
            self.env['audit.log.report'].create_log(rec, values, action='write')
        
        # Chamar o método original de 'write'
        return super(InformaCursos, self).write(values)

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
        return super(InformaCursos, self).unlink()