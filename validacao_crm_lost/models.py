from odoo import models, fields, api, exceptions


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.constrains('stage_id')
    def _check_stage_id(self):
        for lead in self:
            if lead.stage_id.name == 'Perdemos' and not lead.lost_reason:
                raise exceptions.ValidationError('Para mover o lead para "Perdemos", uma razão precisa ser especificada.')
