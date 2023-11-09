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

    message = fields.Text(string='Mensagem', readonly=True)
    proceed_with_creation = fields.Boolean(string="Prosseguir com a criação?")

    def action_confirm(self):
        context = dict(self._context)
        if self.proceed_with_creation:
            context['proceed_with_creation'] = True
        return {'type': 'ir.actions.act_window_close', 'context': context}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}