from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        if 'active' in vals:
            for record in self:
                state = 'deactivated' if not vals.get('active', True) else 'activated'
                
                # Registrar no histórico de desativação
                self.env['whatsapp_deactivation_history'].create({
                    'model_name': 'res.partner',
                    'record_name': record.name,
                    'state': state,
                    'deactivated_by': self.env.user.id,
                    'deactivation_date': fields.Datetime.now(),
                })
                
        return super(ResPartner, self).write(vals)
