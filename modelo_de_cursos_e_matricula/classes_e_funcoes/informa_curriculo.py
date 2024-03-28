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

class InformaCurriculo(models.Model):
    """
    Esta classe representa os currículos dos cursos.
    """
    _name = 'informa.curriculo'
    _description = 'Informa Curriculo'
    _inherit = ["mail.thread", "mail.activity.mixin"]


    name = fields.Char(string='Nome do curriculo:', required=True, tracking=True)
    professor = fields.Many2one('res.partner', string="Professor", required=True, tracking=True, domain=[('professor', '=', True)])
    cod_curriculo = fields.Char(string='Código do curriculo:', required=True, tracking=True)
    

    _sql_constraints = [
        ('cod_grup_disciplina_unique', 'UNIQUE(curriculo_variant_ids)', 'Cada currículo deve estar associado a uma única variante!')
    ]

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

    @api.model
    def create(self, values):
        # Verifique se o nome do currículo está presente nos valores
        if 'name' in values and not values.get('cod_curriculo'):
            # Obter os 4 primeiros caracteres do nome do currículo
            prefixo = values['name'][:4].upper()
            # Gerar um código aleatório até que seja único
            while True:
                # Gerar 4 dígitos aleatórios
                sufixo = str(random.randint(1000, 9999))
                # Combinar prefixo e sufixo para formar o código
                codigo = f"{prefixo}{sufixo}"
                # Verificar se o código já existe
                if not self.search_count([('cod_curriculo', '=', codigo)]):
                    values['cod_curriculo'] = codigo
                    break
                # Se o código já existe, o loop continuará para gerar um novo código
        elif 'name' not in values:
            raise ValidationError("O nome do currículo é necessário para gerar o código.")

        # Chamar o método original de 'create' com o novo código
        record = super(InformaCurriculo, self).create(values)

        # Log de auditoria
        self.env['audit.log.report'].create_log(record, values, action='create')

        return record

    def write(self, values):
        # Log de auditoria antes da alteração
        for rec in self:
            self.env['audit.log.report'].create_log(rec, values, action='write')
        # Chamar o método original de 'write'
        return super(InformaCurriculo, self).write(values)

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
        return super(InformaCurriculo, self).unlink()