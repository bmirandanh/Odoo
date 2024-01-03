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

class MatriculaReingressoWizard(models.Model):
    _name = 'matricula.reingresso.wizard'
    _description = 'Assistente para Re-ingresso de Matrícula'

    matricula_id = fields.Many2one('informa.matricula', string="Matrícula", readonly=True)
    tipo_de_ingresso = fields.Many2one('tipo.de.ingresso', string="Tipo de Ingresso", required=True)
    justificativa = fields.Text(string="Justificativa", required=True)
    data_inscricao = fields.Date(string="Data de Inscrição", required=True, default=fields.Date.today())

    def confirm_reingresso(self):
        if self.matricula_id:
            allowed_statuses = ['MATRÍCULA CANCELADA', 'FINALIZADO', 'EXPEDIDO', 'TRANCADO']
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