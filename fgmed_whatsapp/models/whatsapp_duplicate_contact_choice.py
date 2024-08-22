from odoo import models, fields, api

class WhatsappDuplicateContactChoice(models.TransientModel):
    _name = 'whatsapp.duplicate.contact.choice'
    _description = 'WhatsApp Duplicate Contact Choice'

    phone_number = fields.Char(string='Phone Number', required=True, readonly=True)
    contact_ids = fields.Many2many('res.partner', string='Contacts', required=True)  # Mostrar apenas contatos com o número duplicado, sem edição
    selected_contact_id = fields.Many2one(
        'res.partner', 
        string='Selected Contact', 
        domain="[('id', 'in', contact_ids)]",  # Restringe a seleção apenas aos contatos com o mesmo número de telefone      
    )
    wizard_id = fields.Many2one('whatsapp.duplicate.contact.wizard', string='Wizard Reference', required=True)
