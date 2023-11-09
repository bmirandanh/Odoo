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
    color = fields.Integer(string='Color Index')
    