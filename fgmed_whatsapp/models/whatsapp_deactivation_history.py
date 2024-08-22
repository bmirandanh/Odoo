from odoo import models, fields

class WhatsappDeactivationHistory(models.Model):
    _name = 'whatsapp_deactivation_history'
    _description = 'Deactivation History'

    model_name = fields.Char(string='Model Name', required=True)
    record_name = fields.Char(string='Record Name', required=True)
    state = fields.Selection([('activated', 'Activated'), ('deactivated', 'Deactivated')], string='State', required=True)
    deactivated_by = fields.Many2one('res.users', string='Deactivated By', required=True)
    deactivation_date = fields.Datetime(string='Date/Time', required=True, default=fields.Datetime.now)
