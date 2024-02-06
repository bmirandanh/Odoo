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

class Disciplina(models.Model):
    _name = 'informa.disciplina'
    _description = 'Disciplina'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Nome da Disciplina', required=True)
    media = fields.Float(string='Média para Aprovação')
    grupo_disciplina_id = fields.Many2one('informa.curriculo', string='Grupo de Disciplinas')
    cod_disciplina = fields.Char(string='Código único de disciplina: ', required=True)
    
    def _check_cod_disciplina_in_odoo(self, cod_disciplina):
        existing_disciplina = self.env['informa.disciplina'].search([('cod_disciplina', '=', cod_disciplina)], limit=1)
        if existing_disciplina:
            _logger.info(f"A disciplina com código {cod_disciplina} já existe no Odoo com ID {existing_disciplina.id}.")
            return True
        return False

    def _check_name_in_odoo(self, name):
        existing_disciplina = self.env['informa.disciplina'].search([('name', '=', name)], limit=1)
        if existing_disciplina:
            _logger.info(f"Uma disciplina com o nome {name} já existe no Odoo com ID {existing_disciplina.id}.")
            return True
        return False    
    
    @api.constrains('media')
    def _check_media(self):
        for record in self:
            if record.media < 0 or record.media > 10:
                raise ValidationError(_("A média deve estar entre 0 e 10."))
            
    @api.model
    def create(self, vals):
        cod_disciplina = vals.get('cod_disciplina')
        name = vals.get('name')

        if IS_TEST_ENVIRONMENT:
            exists_cod_in_odoo = self._check_cod_disciplina_in_odoo(cod_disciplina)
            exists_name_in_odoo = self._check_name_in_odoo(name)
            
            if exists_cod_in_odoo:
                raise ValidationError(_("Uma disciplina com este código já existe no Odoo."))

            if exists_name_in_odoo:
                raise ValidationError(_("Uma disciplina com este nome já existe no Odoo."))

        else:
            self._connect_moodle()
            exists_cod_in_odoo = self._check_cod_disciplina_in_odoo(cod_disciplina)
            exists_name_in_odoo = self._check_name_in_odoo(name)
            exists_cod_in_moodle = self._check_if_exists_in_moodle(cod_disciplina)
            exists_name_in_moodle = self._check_name_in_moodle(name)
            
            if exists_cod_in_odoo:
                raise ValidationError(_("Uma disciplina com este código já existe no Odoo."))

            if exists_name_in_odoo:
                raise ValidationError(_("Uma disciplina com este nome já existe no Odoo."))

            if exists_cod_in_moodle:
                _logger.info(f"A disciplina com código {cod_disciplina} já existe no Moodle.")
                raise ValidationError(_("Uma disciplina com este código já existe no Moodle."))

            if exists_name_in_moodle:
                _logger.info(f"Uma disciplina com o nome {name} já existe no Moodle.")
                raise ValidationError(_("Uma disciplina com este nome já existe no Moodle."))

        disciplina = super().create(vals)
        
        self._send_to_moodle(disciplina)

        _logger.info(f"Disciplina {name} (código: {cod_disciplina}) criada com sucesso no Odoo com ID {disciplina.id}.")
        
        return disciplina

    def _connect_moodle(self):
        moodle_url = "https://avadev.medflix.club/webservice/rest/server.php"
        moodle_token = "c502156af2c00a4b3e9e5d878922be46"
        moodle = Moodle(moodle_url, moodle_token)
        return moodle

    def _send_to_moodle(self, disciplina):
        if IS_TEST_ENVIRONMENT:
            _logger.info(f"Simulando envio de disciplina {disciplina.name} para Moodle.")
            return

        base_url = "https://avadev.medflix.club/webservice/rest/server.php"
        token = "c502156af2c00a4b3e9e5d878922be46"
        
        # Construindo o endpoint
        params = {
            "wstoken": token,
            "wsfunction": "core_course_create_courses",
            "moodlewsrestformat": "json",
            "courses[0][shortname]": disciplina.cod_disciplina,
            "courses[0][fullname]": disciplina.name,
            "courses[0][idnumber]": disciplina.id,
            "courses[0][categoryid]": 1  # enviar categoryid como 1
        }

        response = requests.post(base_url, params=params)
        
        if response.status_code == 200:
            _logger.info(f"Disciplina {disciplina.name} enviada com sucesso para o Moodle.")
            _logger.info(f"Resposta do Moodle ao criar a Disciplina: {response.text}")
        else:
            _logger.error(f"Erro ao enviar disciplina {disciplina.name} para o Moodle. Resposta: {response.text}")

    def _check_if_exists_in_moodle(self, cod_disciplina):
        moodle = self._connect_moodle()
        # Supondo que o método para buscar cursos seja core_course_get_courses
        courses = moodle('core_course_get_courses')  # Obtém todos os cursos

        # Verifique se o curso com o cod_disciplina específico existe na lista de cursos
        for course in courses:
            if course['shortname'] == cod_disciplina:
                return True

        return False

    def _check_name_in_moodle(self, name):
        moodle = self._connect_moodle()
        courses = moodle('core_course_get_courses')

        for course in courses:
            if course['fullname'] == name:
                return True

        return False
            
                    