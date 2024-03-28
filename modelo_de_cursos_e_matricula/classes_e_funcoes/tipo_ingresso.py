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
        
class TipoIngresso(models.Model):
    _name = 'tipo.de.ingresso'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Tipo de Ingresso'
    _rec_name = 'nome'
    
    nome = fields.Char(string="nome", required=True, tracking=True)
    descricao = fields.Char(string="descrição", required=True, tracking=True)
    color = fields.Integer(string='Color Index', tracking=True)
    cod_ingresso = fields.Char(string='Código do ingresso', tracking=True, readonly=True)
    
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
        # Verificar se o nome está presente nos valores
        if 'nome' in values:
            # Obter os 4 primeiros caracteres do nome
            prefixo = values['nome'][:4].upper()
            # Gerar um código aleatório até que seja único
            while True:
                # Gerar 4 dígitos aleatórios
                sufixo = str(random.randint(1000, 9999))
                # Combinar prefixo e sufixo para formar o código
                codigo = f"{prefixo}{sufixo}"
                # Verificar se o código já existe
                if not self.search_count([('cod_ingresso', '=', codigo)]):
                    values['cod_ingresso'] = codigo
                    break
                # Se o código já existe, o loop continuará para gerar um novo código
        else:
            raise ValidationError("O nome do Tipo de Ingresso é necessário para gerar o código.")

        # Chamar o método original de 'create' com o novo código
        record = super(TipoIngresso, self).create(values)

        # Log de auditoria
        self.env['audit.log.report'].create_log(record, values, action='create')

        return record

    def write(self, values):
        # Log de auditoria antes da alteração
        for rec in self:
            self.env['audit.log.report'].create_log(rec, values, action='write')
        # Chamar o método original de 'write'
        return super(TipoIngresso, self).write(values)

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
        return super(TipoIngresso, self).unlink()