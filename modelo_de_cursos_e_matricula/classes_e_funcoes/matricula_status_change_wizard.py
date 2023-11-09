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
                self.matricula_id.data_original_certificacao = date.today() + relativedelta(months=48)
                self.matricula_id.prazo_exp_certf_dias = "Matrícula Cancelada"
                # Altera o tipo de cancelamento selecionado para a matrícula
                self.matricula_id.tipo_de_cancelamento = self.tipo_de_cancelamento    
                # Altera o color_tipo_cancelamento pelo color do tipo de cancelamento selecionado
                self.matricula_id.color_tipo_cancelamento = self.tipo_de_cancelamento.color

                    
            # Registra a justificativa como uma mensagem de rastreamento na matrícula
            self.matricula_id.message_post(body=_("Justificativa para alteração de status: %s") % (self.justificativa,))