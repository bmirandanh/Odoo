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
    tempo_de_conclusao = fields.Selection([('03M/90D', '03M/90D'), ('06M', '06M'), ('12M', '12M'), ('24M', '24M'), ('36M', '36M'), ('48M', '48M')], string="Tempo de conclusão", required=True, tracking=True)
    formato_nota = fields.Selection([
    ('normal', '0-10'),
    ('porcentagem', '0-100 (%)')
    ], string='Formato da Nota', default='normal', tracking=True, required=True)
    
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