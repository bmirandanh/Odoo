from odoo import models, fields, api, _
from odoo.exceptions import AccessError

class AuditLogReport(models.Model):
    _name = 'audit.log.report'
    _description = 'Relatório de Auditoria de Logs'

    model_name = fields.Char(string="Modelo")
    action = fields.Char(string="Ação")
    field_name = fields.Char(string="Campo Alterado", help="Para ações de criação, este campo pode ficar vazio.")
    old_value = fields.Char(string="Valor Antigo", help="Para ações de criação, este campo pode ficar vazio.")
    new_value = fields.Char(string="Valor Novo")
    user_id = fields.Many2one('res.users', string="Usuário Responsável", default=lambda self: self.env.user)
    change_date = fields.Datetime(string="Data da Mudança", default=fields.Datetime.now)
    model_code = fields.Char(string="Código do Modelo")
    
    def _get_model_code_field(self, model_name):
        """Retorna o nome do campo de código com base no nome do modelo."""
        code_fields = {
            'tipo.de.ingresso': 'cod_ingresso',
            'informa.disciplina': 'cod_disciplina',
            'informa.curriculo': 'cod_curriculo',
            'informa.curriculo.variant': 'cod_variante',
            'informa.cursos' : 'cod_curso',
            'informa.matricula' : 'numero_matricula',
            'registro_disciplina':'matriculas_ids.numero_matricula',
            'res.partner' : 'matriculas_ids',
        }
        return code_fields.get(model_name, '')

    def create_log(self, record, values, action):
        model_name = record._name
        user_id = self.env.user.id
        change_date = fields.Datetime.now()
        # Obter o nome do campo de código para o modelo, se houver
        code_field = self._get_model_code_field(model_name)
        model_code = getattr(record, code_field, '') if code_field else 'N/A'
        
        if action in ['create', 'write']:
            for field_name in values.keys():
                # Para ação de criação, não teremos um 'old_value'
                old_value = getattr(record, field_name, '') if action == 'write' else ''
                new_value = values[field_name]

                # Verificar se o novo valor é um many2one e armazenar apenas o ID para simplificação
                if isinstance(new_value, models.BaseModel):
                    new_value = new_value.id

                log_vals = {
                    'model_code' : str(model_code),
                    'model_name': model_name,
                    'action': action,
                    'field_name': field_name,
                    'old_value': str(old_value) if old_value else '',
                    'new_value': str(new_value),
                    'user_id': user_id,
                    'change_date': change_date,
                }
                self.create(log_vals)
        elif action == 'unlink':
            # Para ações de exclusão, podemos não ter detalhes de campo específicos
            log_vals = {
                'model_code' : str(model_code),
                'model_name': model_name,
                'action': action,
                'field_name': '',
                'old_value': '',
                'new_value': 'Registro Excluído',
                'user_id': user_id,
                'change_date': change_date,
            }
            self.create(log_vals)

    def write(self, vals):
        # Bloquear alterações nos registros existentes
        raise AccessError(_("Os registros de auditoria não podem ser modificados."))

    def unlink(self):
        # Bloquear exclusões de registros
        raise AccessError(_("Os registros de auditoria não podem ser excluídos."))