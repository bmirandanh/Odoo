# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class FgmedCoursePaymentTerm(models.Model):
    _inherit = "account.payment.term"
    @api.onchange('line_ids')
    def set_total_lines(self):
        for rec in self:
            if rec.line_ids:
                totalLines = 0
                for item in self.line_ids:
                    totalLines = totalLines + 1
                rec.payment_term_count = totalLines

    payment_term_type = fields.Selection([('checkout', 'Checkout Cartão de Crédito'),('recurrence', 'Recorrência'),('future-recurrence', 'Recorrência Futura'),('checkout-misto', 'Checkout Misto'),('checkout-pix', 'Checkout Pix'),('signment', 'Assinatura')], string="Forma de pagamento")
    payment_term_count = fields.Integer(string='Número de parcelas')

class FgmedCustomProductFields(models.Model):
    _inherit = "product.product"

    course_conclusion = fields.Char(string='Tempo de conclusão do curso')
    course_modality = fields.Selection([('intensiva', 'Intensiva'),('extensiva', 'Extensiva'),('ouro', 'Ouro')], string="Modalidade do curso")
    course_base_time_id = fields.Many2one(
        'fgmed.courses.time', string='Tempo Base (h/a)')
    course_itrn_time_id = fields.Many2one(
        'fgmed.courses.time', string='Tempo de Estágio (h/a)')
    course_payment_methods_ids = fields.Many2many(
        'account.payment.term', string='Condições de pagamento aceitas')


class FgmedCourseBaseTimes(models.Model):
    _name = 'fgmed.courses.time'
    _description = 'Tempo base para conclusão dos cursos'

    name = fields.Char(string='Nome da modalidade')
    time = fields.Integer(string='Tempo em horas da modalidade')
    

class ProductTag(models.Model):
    _name = 'product.tag'
    _description = 'Product Tag'

    name = fields.Char(string='Tag Name')
    color = fields.Integer(string='Color Index')
    
    def action_open_tags(self):
        return {
            'name': 'Open Tags',
            'type': 'ir.actions.act_window',
            'res_model': 'product.tag',
            'view_mode': 'tree,form',
        }

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_tags = fields.Many2many('product.tag', string='Tags')

