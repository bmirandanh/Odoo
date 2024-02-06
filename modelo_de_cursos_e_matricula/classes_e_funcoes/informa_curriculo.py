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
    cod_curriculo = fields.Char(string='Código do curriculo:', required=True, tracking=True)

    _sql_constraints = [
        ('cod_grup_disciplina_unique', 'UNIQUE(curriculo_variant_ids)', 'Cada currículo deve estar associado a uma única variante!')
    ]