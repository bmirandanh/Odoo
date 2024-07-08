from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class InformaCertificado(models.TransientModel):
    _name = 'informa.certificado'
    _description = 'Certificate Wizard'

    student_id = fields.Many2one('res.partner', string='Aluno', required=True)
    enrollment_id = fields.Many2one('informa.matricula', string='Matrícula do Aluno', required=True)
    nome_do_aluno = fields.Many2one(related='enrollment_id.nome_do_aluno', string='Nome do aluno', readonly=True)
    curso = fields.Many2one(related='enrollment_id.curso', string='Curso', readonly=True)
    total_duracao_horas_id = fields.Float(related='curso.total_duracao_horas', string='Duração(H): ', readonly=True)
    data_certificacao = fields.Date(string='Data de Certificação')
    template_id = fields.Selection([
        ('certificate_template_1', 'Template 1'),
        ('certificate_template_2', 'Template 2')
    ], string='Template do Certificado', required=True, default='certificate_template_1')
    matricula_line_ids = fields.One2many(
        'informa.matricula.line', 'matricula_id', string='Disciplinas', readonly=True
    )
    
    
    
    def generate_certificate(self):
        self.ensure_one()

        matricula = self.enrollment_id
        registro_disciplina = self.env['informa.registro_disciplina'].search([('matricula_id', '=', matricula.id)], limit=1)
        
        if not registro_disciplina:
            _logger.error(f"Nenhum registro de disciplina encontrado para a matrícula ID: {matricula.id}")
            raise UserError('Nenhum registro de disciplina encontrado para esta matrícula.')

        if matricula.status_do_certificado != 'FINALIZADO':
            _logger.warning(f"Certificado não pode ser gerado para a matrícula ID: {matricula.id} com status {matricula.status_do_certificado}")
            raise UserError('Certificados só podem ser gerados para matrículas com status FINALIZADO.')

        # Atualizar o status conforme necessário
        if matricula.status_do_certificado == 'FINALIZADO':
            matricula.write({'status_do_certificado': 'EXPEDIDO'})
        elif matricula.status_do_certificado == 'EXPEDIDO':
            matricula.write({'status_do_certificado': 'EXPEDIDO SEGUNDA VIA'})
        
        _logger.info(f'Status do certificado atualizado para {matricula.status_do_certificado} no registro de disciplina ID: {registro_disciplina.id}')

        # Chamar a ação de relatório conforme o template escolhido
        report_action_id = f"modelo_de_cursos_e_matricula.action_report_{self.template_id}"
        try:
            return self.env.ref(report_action_id).report_action(matricula)
        except ValueError:
            raise UserError(f"Ação de relatório não encontrada para o template ID: {self.template_id}")
