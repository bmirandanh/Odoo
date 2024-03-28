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
    cod_variante = fields.Char(string='Código da variente', tracking=True)
    
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
    @api.constrains('curriculo_ids')
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

    @api.model
    def create(self, values):
        # Verificar se um código para a variante não foi fornecido nos valores
        if 'cod_variante' not in values or not values['cod_variante']:
            # Gerar um código aleatório até que seja único
            while True:
                # Gerar 4 dígitos aleatórios
                sufixo = str(random.randint(1000, 9999))
                # Combinar o sufixo com algum prefixo ou lógica específica para formar o código
                # Por exemplo, você pode querer usar uma parte do nome do currículo ou a data de criação
                codigo = f"VAR{sufixo}"
                # Verificar se o código já existe
                if not self.search_count([('cod_variante', '=', codigo)]):
                    values['cod_variante'] = codigo
                    break
                # Se o código já existe, o loop continuará para gerar um novo código
        else:
            # Se o cod_variante foi fornecido, apenas verifique se é único
            if self.search_count([('cod_variante', '=', values['cod_variante'])]):
                raise ValidationError("O código da variante fornecido já existe.")

        # Chamar o método original de 'create' com o novo código
        record = super(InformaCurriculoVariant, self).create(values)

        # Log de auditoria
        self.env['audit.log.report'].create_log(record, values, action='create')

        return record

    def write(self, values):
        # Log de auditoria antes da alteração
        for rec in self:
            self.env['audit.log.report'].create_log(rec, values, action='write')
        # Chamar o método original de 'write'
        return super(InformaCurriculoVariant, self).write(values)

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
        return super(InformaCurriculoVariant, self).unlink()