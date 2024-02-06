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


class InformaCurriculoVariant(models.Model):
    """
    Esta classe representa as variantes dos currículos.
    """
    _name = 'informa.curriculo.variant'
    _description = 'Variantes do Currículo'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Nome', required=True, tracking=True)
    create_date = fields.Datetime(string='Data de Criação', readonly=True, default=lambda self: fields.Datetime.now(), tracking=True)
    variation_number = fields.Integer(string='Número da Variação', readonly=True, compute='_compute_variation_number', tracking=True)
    disciplina_ids = fields.Many2many('informa.disciplina', string='Disciplinas', tracking=True)
    sequence = fields.Integer(string='Sequência', help="Determina a ordem de exibição dos grupos.", tracking=True)
    days_to_release = fields.Integer(string="Dias para Liberação", default=7, help="Número de dias para liberar as disciplinas deste grupo.", tracking=True)
    default_days_to_release = fields.Integer(string="Dias para Liberação", default=7, help="Número de dias para liberar as disciplinas do próximo grupo.", tracking=True)
    curriculo_id = fields.Many2one('informa.curriculo', string='Currículo', tracking=True)

    @api.constrains('curriculo_ids=')
    def _check_curriculo_id(self):
        for variant in self:
            if not variant.curriculo_id:
                raise ValidationError("O campo 'Currículo' deve ser preenchido.")

    @api.depends('create_date')
    def _compute_variation_number(self):
        for variant in self:
            variant_count = len(self.filtered(lambda v: v.create_date <= variant.create_date))
            variant.variation_number = variant_count

    def decrement_days_to_release(self):
        for record in self:
            if record.days_to_release > 0:
                record.days_to_release -= 1

    def release_next_group(self):
        # Busque o grupo de disciplinas pela sequência atual
        current_group = self.env['informa.curriculo'].search([('sequence', '=', self.current_sequence)], limit=1)

        # Se não encontrou um grupo ou já liberou todas as sequências, retorne
        if not current_group:
            return []

        # Se a data atual for maior ou igual a next_release_date, avance para o próximo grupo
        if fields.Date.today() >= current_group.next_release_date:
            self.current_sequence += 1
            return current_group

        return []            