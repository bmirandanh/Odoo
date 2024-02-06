from odoo import api, fields, models, _
import logging


IS_TEST_ENVIRONMENT = False
_logger = logging.getLogger(__name__)

class TipoCancelamento(models.Model):
    _name = 'tipo.de.cancelamento'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Tipo de Suspensão'
    _rec_name = 'nome'

    nome = fields.Char(string="nome", required=True)
    descricao = fields.Char(string="descrição", required=True, tracking=True)
    color = fields.Integer(string='Color Index')
