from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import uuid

class InformaMatriculaLine(models.Model):
    _name = 'informa.matricula.line'
    _description = 'Linha de Matrícula'

    matricula_id = fields.Many2one(
        'informa.matricula',
        string='Matrícula',
        ondelete='cascade',
        required=True
    )
    disciplina_id = fields.Many2one(
        'informa.disciplina',
        string='Disciplina',
        required=True
    )
    nome_disciplina = fields.Char(
        related='disciplina_id.name',
        string='Nome da Disciplina',
        readonly=True
    )
    cod_disciplina = fields.Char(
        related='disciplina_id.cod_disciplina',
        string='Código da Disciplina',
        readonly=True
    )
    professor_id = fields.Many2one(
        related='disciplina_id.professor',
        string='Professor',
        readonly=True
    )
    media_necessaria = fields.Float(
        related='disciplina_id.media',
        string='Média para Aprovação',
        readonly=True
    )
    registro_disciplina_id = fields.Many2one(
        'informa.registro_disciplina',
        string='Registro',
        readonly=True,
        domain="[('matricula_id', '=', matricula_id)]"
    )
    nota = fields.Float(
        string='Nota',
        readonly=True
    )
    
    # Novo campo para armazenar o número da matrícula para referência fácil
    numero_matricula = fields.Char(related='matricula_id.numero_matricula', string='Número de Matrícula', readonly=True, store=True)

    # Adicione um novo campo para a referência única
    line_ref = fields.Char(string='Referência da Linha', readonly=True, copy=False)

    @api.model
    def create(self, vals):
        """
        Cria uma nova linha de matrícula. Este método é chamado quando uma nova
        linha de matrícula é criada a partir do ORM. O campo 'matricula_id' é
        obrigatório, assim como o campo 'disciplina_id'.
        """
        if 'matricula_id' not in vals or 'disciplina_id' not in vals:
            raise ValidationError("Os campos 'matricula_id' e 'disciplina_id' são obrigatórios.")
        
        # O número da matrícula deve ser copiado do registro de matrícula relacionado
        matricula_record = self.env['informa.matricula'].browse(vals['matricula_id'])
        vals['numero_matricula'] = matricula_record.numero_matricula
        
        # Use o número da matrícula e o código da disciplina para criar a referência da linha
        disciplina_code = self.env['informa.disciplina'].browse(vals['disciplina_id']).cod_disciplina
        vals['line_ref'] = f'{vals["numero_matricula"]}/{disciplina_code}'

        return super(InformaMatriculaLine, self).create(vals)


    def unlink(self):
        """
        Sobrescrita do método unlink para impedir a exclusão das linhas de
        matrícula depois de criadas.
        """
        raise ValidationError("Não é permitido remover as disciplinas de uma matrícula existente.")
