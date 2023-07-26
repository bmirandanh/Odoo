from odoo import models, fields, api

class MailMail(models.Model):
    _inherit = 'mail.mail'

    body_html = ''

class ProductTag(models.Model):
    _name = 'product.tag'
    _description = 'Product Tag'

    name = fields.Char(string='Tag Name')
    color = fields.Integer(string='Color Index')

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_tags = fields.Many2many('product.tag', string='Tags')

    def action_open_tags(self):
        return {
            'name': 'Open Tags',
            'type': 'ir.actions.act_window',
            'res_model': 'product.tag',
            'view_mode': 'tree,form',
        }
   