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

class MatriculaConfirmationWizard(models.TransientModel):
    _name = 'informa.matricula.confirmation.wizard'
    _description = 'Wizard para Confirmar a Criação de Matrícula'

    message = fields.Text(string='Mensagem', readonly=True, tracking=True)
    proceed_with_creation = fields.Boolean(string="Prosseguir com a criação?", tracking=True)

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

    def action_confirm(self):
        context = dict(self._context)
        if self.proceed_with_creation:
            context['proceed_with_creation'] = True
        return {'type': 'ir.actions.act_window_close', 'context': context}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def create(self, values):
        # Chamar o método original de 'create'
        record = super(MatriculaConfirmationWizard, self).create(values)
        # Log de auditoria
        self.env['audit.log.report'].create_log(record, values, action='create')
        return record

    def write(self, values):
        # Log de auditoria antes da alteração
        for rec in self:
            self.env['audit.log.report'].create_log(rec, values, action='write')
        # Chamar o método original de 'write'
        return super(MatriculaConfirmationWizard, self).write(values)

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
        return super(MatriculaConfirmationWizard, self).unlink()     