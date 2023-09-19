from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import date
import random
from odoo import tools
import logging
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class InformaCursos(models.Model):
    _name = 'informa.cursos'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Cursos'

    name = fields.Char(string='Nome do curso',  required=True, tracking=True, domain=[('aluno', '=', True)])
    status_do_certificado = fields.Selection(related='matricula_id.status_do_certificado', readonly=True)
    numero_matricula = fields.Char(related='matricula_id.numero_matricula', readonly=True)
    matricula_id = fields.Many2many('informa.matricula', 'curso', string="Matrículas", readonly=True)
    cod_curso = fields.Char(string='Código do Curso', tracking=True)
    grupo_disciplina_id = fields.Many2many('informa.grupo_disciplina', string='Grupo de Disciplina')
    disciplina_ids = fields.Many2many('informa.disciplina', string='Disciplinas')
    tempo_de_conclusao = fields.Selection([('03M/90D', '03M/90D'), ('06M', '06M'), ('12M', '12M'), ('24M', '24M'), ('36M', '36M'), ('48M', '48M')], string="Tempo de conclusão", required=True, tracking=True)

    
    def action_open_courses(self):
        # Buscar o registro pelo nome
        curso = self.env['informa.cursos'].search([('name', '=', self.name)], limit=1)
        
        # Se o registro foi encontrado
        if curso:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Detalhes do Curso',
                'res_model': 'informa.cursos',
                'view_mode': 'form',
                'res_id': curso.id,   # ID do registro encontrado
                'target': 'current',
            }
        else:
            # Opcional: Você pode retornar um aviso se o registro não for encontrado.
            return {
                'warning': {
                    'title': "Aviso",
                    'message': "Curso não encontrado!"
                }
            }

class GrupoDisciplina(models.Model):
    _name = 'informa.grupo_disciplina'
    _description = 'Grupo de Disciplinas'

    name = fields.Char(string='Nome do Grupo: ', required=True)
    disciplina_ids = fields.Many2many('informa.disciplina', string="Disciplinas")

class Sequencia(models.Model):
    _name = 'informa.sequencia'
    _description = 'Sequencia de Disciplinas'
    _order = 'sequence'  # Para garantir que eles sejam buscados na ordem correta

    name = fields.Char('Nome da Sequencia')
    sequence = fields.Integer('Sequência')
    grupo_disciplina_id = fields.Many2one('informa.grupo_disciplina', string='Grupo de Disciplina')
    curso_id = fields.Many2one('informa.cursos', string="Curso Relacionado")
    
class InformaMatricula(models.Model):
    _name = 'informa.matricula'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Matriculas'
    
    status_do_certificado = fields.Selection(
        [('CURSANDO','CURSANDO'),
        ('EM FINALIZAÇÃO','EM FINALIZAÇÃO'),
        ('FINALIZADO','FINALIZADO'),
        ('EM PRAZO EXCEDIDO','EM PRAZO EXCEDIDO'),
        ('EXPEDIDO','EXPEDIDO'),
        ('MATRÍCULA CANCELADA','MATRÍCULA CANCELADA'),
        ],
        compute='_compute_status_certificado', default="CURSANDO", store=True, tracking=True
    )
    regiao = fields.Selection([
        ('AVA','AVA'),
        ('PRESENCIAL','PRESENCIAL'),
        ] , required=True, tracking=True)
    justificativa_cancelamento = fields.Text(string="Justificativa de Cancelamento", tracking=True)
    inscricao_ava = fields.Date(string='Inscrição Ava', required=True, tracking=True)
    email = fields.Char(string="Email", tracking=True)
    telefone = fields.Char(string="Telefone", tracking=True)
    nome_do_aluno = fields.Many2one('res.partner', string="Aluno", required=True, tracking=True, domain=[('aluno', '=', True)])
    curso = fields.Many2one('informa.cursos', string="Curso", required=True, tracking=True)
    prazo_exp_certf_dias = fields.Char(compute='_compute_prazo_exp_certf_dias', string='Prazo exp. Certf. Em dias', tracking=True)
    numero_de_modulo = fields.Char(compute='_compute_numero_de_modulo', tracking=True, string='Nº de Módulo', store=True)
    data_provavel_certificacao = fields.Date(compute='_compute_data_provavel_certificacao', tracking=True, string='Data provável de certificação', store=True)
    tipo_de_ingresso = fields.Many2one('tipo.de.ingresso', string="Tipo de ingresso", required=True, tracking=True)
    tipo_de_cancelamento = fields.Many2one('tipo.de.cancelamento', string="Tipo de Cancelamento", tracking=True)
    color_tipo_ingresso = fields.Integer(related='tipo_de_ingresso.color', string='Color Index from Tipo de Ingresso')
    color_tipo_cancelamento = fields.Integer(related='tipo_de_cancelamento.color', string='Color Index from Tipo de Cancelamento')
    numero_matricula = fields.Char(string="Número de Matrícula", readonly=True)
    matricula_aluno = fields.Char(related='nome_do_aluno.matricula_aluno', string="Matrícula do Aluno", readonly=True)
    cod_curso = fields.Char(compute='_compute_cod_curso', string="Código do Curso", tracking=True, store=True)
    grupo_disciplina_id = fields.Many2one('informa.grupo_disciplina', string='Grupo de Disciplina')
    disciplina_ids = fields.Many2many('informa.registro_disciplina', string='Disciplinas')
    
    def atualizar_status_matricula(self):
        for matricula in self:
            registros_disciplina = self.env['informa.registro_disciplina'].search([('matricula_id', '=', matricula.id)])
            if all(record.status == 'aprovado' for record in registros_disciplina):
                matricula.status_do_certificado = 'FINALIZADO'
        
    @api.model
    def create(self, vals):
        # Primeiro, verifique se o aluno já tem uma matrícula no curso especificado.
        aluno_id = vals.get('nome_do_aluno')
        curso_id = vals.get('curso')
        existing_matricula = self.search([('nome_do_aluno', '=', aluno_id), ('curso', '=', curso_id)])

        if existing_matricula:
            raise UserError(_('O aluno já possui uma matrícula neste curso!'))

        # Se não houver matrícula existente, crie a nova matrícula.
        matricula_record = super(InformaMatricula, self).create(vals)
        
        # Pegue as disciplinas permitidas para o curso associado à matrícula.
        allowed_disciplinas = self.compute_allowed_disciplinas(matricula_record.curso)
        
        # Para cada disciplina permitida, crie um novo registro de 'RegistroDisciplina'.
        for disciplina in allowed_disciplinas:
            if disciplina.id:
                self.env['informa.registro_disciplina'].create({
                    'aluno_id': matricula_record.nome_do_aluno.id,
                    'curso_id': matricula_record.curso.id,
                    'matricula_id': matricula_record.id,
                    'disciplina_id': disciplina.id
                })

        return matricula_record
    
    def compute_allowed_disciplinas(self, curso_id):
        # Buscar todas as disciplinas associadas aos grupos de disciplinas do curso selecionado
        disciplinas = self.env['informa.disciplina']
        for grupo in curso_id.grupo_disciplina_id:
            disciplinas |= grupo.disciplina_ids
        return disciplinas

    def show_student_disciplines(self):
        self.ensure_one()

        domain = [
            ('aluno_id', '=', self.nome_do_aluno.id),
            ('curso_id', '=', self.curso.id)
        ]

        return {
            'name': 'Disciplinas de ' + str(self.nome_do_aluno.name),
            'type': 'ir.actions.act_window',
            'res_model': 'informa.registro_disciplina',
            'view_mode': 'tree',
            'view_id': self.env.ref('modelo_de_cursos_e_matricula.view_registro_disciplina_tree').id,
            'domain': domain,
            'context': {
                'default_aluno_id': self.nome_do_aluno.id,
                'default_curso_id': self.curso.id
            }
        }
                
    @api.onchange('nome_do_aluno')
    def _onchange_nome_do_aluno(self):
    # Se o campo nome_do_aluno não estiver definido, apenas retorne.
        if not self.nome_do_aluno:
            self.email = False
            self.telefone = False
            return

        # Atualiza os campos email e telefone com os valores do aluno selecionado.
        self.email = self.nome_do_aluno.email
        self.telefone = self.nome_do_aluno.phone
           
    @api.depends('curso')
    def _compute_cod_curso(self):
        for record in self:
            record.cod_curso = record.curso.cod_curso if record.curso else False
    
    @api.onchange('cod_curso', 'nome_do_aluno', 'inscricao_ava')
    def _onchange_cod_curso(self):
        # Se nome_do_aluno, inscricao_ava ou cod_curso não estiverem definidos, apenas retorne.
        if not self.nome_do_aluno or not self.inscricao_ava or not self.cod_curso:
            return
        
        # Caso contrário, atualize numero_matricula.
        self.numero_matricula = self._generate_matricula()

    def _generate_matricula(self):
        # Verifica se cod_curso não está vazio.
        if not self.cod_curso:
            raise UserError('Por favor, preencha o Código do Curso antes de gerar a matrícula.')
        
        # Pegar os 7 últimos dígitos do campo matricula_aluno do aluno selecionado
        last_digits = self.nome_do_aluno.matricula_aluno[-7:] if self.nome_do_aluno.matricula_aluno else ''
        
        if not last_digits or len(last_digits) < 7:
            raise UserError('O campo matricula_aluno do aluno selecionado está incorreto ou não definido.')

        # Combina tudo
        matricula = f"{self.cod_curso}{last_digits}"
        return matricula
    
    @api.depends('numero_de_modulo', 'inscricao_ava')
    def _compute_data_provavel_certificacao(self):
        for record in self:
            if record.inscricao_ava:
                if record.numero_de_modulo == '03M/90D':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=3)
                elif record.numero_de_modulo == '06M':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=6)
                elif record.numero_de_modulo == '12M':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=12)
                elif record.numero_de_modulo == '24M':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=24)
                elif record.numero_de_modulo == '36M':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=36)
                elif record.numero_de_modulo == '48M':
                    record.data_provavel_certificacao = record.inscricao_ava + relativedelta(months=48)
                else:
                    record.data_provavel_certificacao = False
            else:
                record.data_provavel_certificacao = False

    @api.depends('curso.tempo_de_conclusao')
    def _compute_numero_de_modulo(self):
        for record in self:
            record.numero_de_modulo = record.curso.tempo_de_conclusao or False
            
    @api.depends('status_do_certificado', 'data_provavel_certificacao', 'inscricao_ava')
    def _compute_prazo_exp_certf_dias(self):
        for record in self:
            if record.status_do_certificado == 'EXPEDIDO':
                record.prazo_exp_certf_dias = "Expedido"
            elif record.status_do_certificado == 'MATRÍCULA CANCELADA':
                record.prazo_exp_certf_dias = "Matrícula Cancelada"
            elif record.status_do_certificado == 'FINALIZADO':
                record.prazo_exp_certf_dias = "Curso Finalizado"
            else:
                if record.inscricao_ava and record.data_provavel_certificacao:
                    dias_passados = (record.data_provavel_certificacao - date.today()).days
                    record.prazo_exp_certf_dias = str(dias_passados) + _(" dias")
                    
                    # Alteração do status baseado no valor de dias_passados
                    if dias_passados <= 0:
                        record.status_do_certificado = 'EM PRAZO EXCEDIDO'
                    elif dias_passados <= 10:
                        record.status_do_certificado = 'EM FINALIZAÇÃO'
                    else:
                        record.status_do_certificado = 'CURSANDO'
                else:
                    record.prazo_exp_certf_dias = _("Data de provável certificação não definida")

    
    def atualizar_status_dias_passados(self):
        records = self.search([])
        for record in records:
            record._compute_prazo_exp_certf_dias()


    def action_open_status_change_wizard(self):
        context = {
            'default_matricula_id': self.id,
        }
        return {
            'name': _('Cancelamento da Matrícula'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'matricula.status.change.wizard',
            'target': 'new',
            'context': context,
        }           

class TipoIngresso(models.Model):
    _name = 'tipo.de.ingresso'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Tipo de Ingresso'
    _rec_name = 'nome'
    
    nome = fields.Char(string="nome", required=True, tracking=True)
    descricao = fields.Char(string="descrição", required=True, tracking=True)
    color = fields.Integer(string='Color Index')
    
class TipoCancelamento(models.Model):
    _name = 'tipo.de.cancelamento'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Tipo de Cancelamento'
    _rec_name = 'nome'

    nome = fields.Char(string="nome", required=True, tracking=True)
    descricao = fields.Char(string="descrição", required=True, tracking=True)
    color = fields.Integer(string='Color Index')
    
            
            
class MatriculaStatusChangeWizard(models.Model):
    _name = 'matricula.status.change.wizard'
    _description = 'Assistente para Alteração de Status da Matrícula'

    matricula_id = fields.Many2one('informa.matricula', string="Matrícula", readonly=True)
    new_status = fields.Selection(
        [
            ('MATRÍCULA CANCELADA', 'MATRÍCULA CANCELADA'),
        ], string="Status", required=True)
    tipo_de_cancelamento = fields.Many2one('tipo.de.cancelamento', string="Tipo de Cancelamento")
    justificativa = fields.Text(string="Justificativa", required=True)

    def change_status(self):
        if self.matricula_id:

            # Lista dos status que podem ser cancelados
            allowed_statuses = ['CURSANDO', 'EM FINALIZAÇÃO', 'EM PRAZO EXCEDIDO']

            # Verificar se o status atual está na lista de status permitidos
            if self.matricula_id.status_do_certificado not in allowed_statuses:
                raise ValidationError(_("Não é possível cancelar uma matrícula com status '%s'.") % self.matricula_id.status_do_certificado)

            if self.new_status == 'MATRÍCULA CANCELADA' and not self.tipo_de_cancelamento:
                raise ValidationError(_("Para cancelar a matrícula, é necessário selecionar um tipo de cancelamento."))

            # Altera o status da matrícula
            self.matricula_id.status_do_certificado = self.new_status

            # Se a matrícula for cancelada
            if self.new_status == 'MATRÍCULA CANCELADA':
                self.matricula_id.justificativa_cancelamento = self.justificativa
                self.matricula_id.data_provavel_certificacao = date.today() + relativedelta(months=48) 
                self.matricula_id.prazo_exp_certf_dias = "Matrícula Cancelada"
                # Altera o tipo de cancelamento selecionado para a matrícula
                self.matricula_id.tipo_de_cancelamento = self.tipo_de_cancelamento    
                # Altera o color_tipo_cancelamento pelo color do tipo de cancelamento selecionado
                self.matricula_id.color_tipo_cancelamento = self.tipo_de_cancelamento.color

                    
            # Registra a justificativa como uma mensagem de rastreamento na matrícula
            self.matricula_id.message_post(body=_("Justificativa para alteração de status: %s") % (self.justificativa,))
            
            
class Disciplina(models.Model):
    _name = 'informa.disciplina'
    _description = 'Disciplina'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Nome da Disciplina', required=True)
    media = fields.Float(string='Média para Aprovação')
    grupo_disciplina_id = fields.Many2one('informa.grupo_disciplina', string='Grupo de Disciplinas')
    

    @api.constrains('media')
    def _check_media(self):
        for record in self:
            if record.media < 0 or record.media > 10:
                raise ValidationError(_("A média deve estar entre 0 e 10."))
            
            
class RegistroDisciplina(models.Model):
    _name = 'informa.registro_disciplina'
    _description = 'Registro de Disciplina do Aluno'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    aluno_id = fields.Many2one('res.partner', string='Aluno', readonly=True, domain=[('is_student', '=', True)])
    curso_id = fields.Many2one('informa.cursos', readonly=True,  string="Curso Relacionado")
    matricula_id = fields.Many2one('informa.matricula', string='Matricula')
    disciplina_id = fields.Many2one('informa.disciplina', string='Disciplina', domain="[('id', 'in', allowed_disciplinas.ids)]")
    disciplina_media = fields.Float(related='disciplina_id.media', string='Média da Disciplina')
    nota = fields.Float(string='Nota do Aluno', store=True)
    status = fields.Selection([('aprovado', 'Aprovado'), ('reprovado', 'Reprovado')], string='Status', compute='_compute_status')
    allowed_disciplinas = fields.Many2many('informa.disciplina', compute='_compute_allowed_disciplinas')
    

    @api.depends('curso_id')
    def _compute_allowed_disciplinas(self):
        for record in self:
            # Buscar todas as disciplinas associadas aos grupos de disciplinas do curso selecionado
            disciplinas = self.env['informa.disciplina']
            for grupo in record.curso_id.grupo_disciplina_id:
                disciplinas |= grupo.disciplina_ids
            
            record.allowed_disciplinas = disciplinas
            
            # Log para ajudar na depuração
            tools.logging.info("Curso: %s", record.curso_id.name)
            tools.logging.info("Grupos de disciplina: %s", record.curso_id.grupo_disciplina_id.mapped('name'))
            tools.logging.info("Disciplinas permitidas: %s", record.allowed_disciplinas.mapped('name'))
        

    @api.depends('nota', 'disciplina_media')
    def _compute_status(self):
        for record in self:
            if record.nota >= record.disciplina_id.media:
                record.status = 'aprovado'
            else:
                record.status = 'reprovado'
    
    @api.constrains('nota')
    def _check_nota(self):
        for record in self:
            if record.nota < 0 or record.nota > 10:
                raise ValidationError(_("A nota deve estar entre 0 e 10."))


    @api.model
    def create(self, vals):
        result = super(RegistroDisciplina, self).create(vals)
        result.matricula_id.atualizar_status_matricula()
        return result

    def write(self, vals):
        result = super(RegistroDisciplina, self).write(vals)
        for record in self:
            record.matricula_id.atualizar_status_matricula()
        return result

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    aluno = fields.Boolean(string="Aluno ?", default=False) 
    matricula_aluno = fields.Char(string="Matrícula do Aluno", readonly=True)
    curso_id = fields.Many2one('informa.curso', string='Curso Atual')
    
    
    @api.onchange('aluno')
    def _onchange_aluno(self):
        # Se 'matricula_aluno' já tiver um valor, não permitimos a modificação
        if self.matricula_aluno:
            return
        
        # Se o campo 'aluno' é marcado e 'matricula_aluno' não tem valor, geramos um número de matrícula
        if self.aluno:
            self.matricula_aluno = self._generate_unique_matricula_aluno()

    def _generate_unique_matricula_aluno(self):
        while True:
            matricula = self._generate_matricula_aluno()
            # Busca no banco de dados para verificar se a matrícula já existe
            existing_partner = self.env['res.partner'].search([('matricula_aluno', '=', matricula)], limit=1)
            
            # Se a matrícula não existir, retorna o valor
            if not existing_partner:
                return matricula

    def _generate_matricula_aluno(self):
        current_year = fields.Date.today().year
        # Determinar o semestre baseado no mês atual
        month = fields.Date.today().month
        semester = '01' if month <= 6 else '02'
        # Gerar os últimos 7 dígitos aleatoriamente
        last_digits = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        return f"{current_year}{semester}{last_digits}"