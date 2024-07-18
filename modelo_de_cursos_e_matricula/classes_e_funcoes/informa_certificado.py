from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
import time

_logger = logging.getLogger(__name__)

class InformaCertificado(models.TransientModel):
    _name = 'informa.certificado'
    _description = 'Certificate Wizard'

    student_id = fields.Many2one('res.partner', string='Aluno', required=True, domain=[('aluno', '=', True)])
    enrollment_id = fields.Many2one('informa.matricula', string='Matrícula do Aluno', required=True)
    nome_do_aluno = fields.Many2one(related='enrollment_id.nome_do_aluno', string='Nome do aluno', readonly=True)
    curso = fields.Many2one(related='enrollment_id.curso', string='Curso', readonly=True)
    total_duracao_horas_id = fields.Float(related='curso.total_duracao_horas', string='Duração(H): ', readonly=True)
    data_certificacao = fields.Date(string='Data de Certificação')
    template_id = fields.Many2one(
        'ir.actions.report', 
        string='Template do Certificado', 
        required=True, 
        default=lambda self: self.env.ref('modelo_de_cursos_e_matricula.action_report_certificate_template_1').id
    )
    matricula_line_ids = fields.One2many(
        'informa.matricula.line', 'matricula_id', string='Disciplinas', readonly=True
    )

    @api.onchange('student_id')
    def _onchange_student_id(self):
        if self.student_id:
            return {'domain': {'enrollment_id': [('nome_do_aluno', '=', self.student_id.id)]}}
        else:
            return {'domain': {'enrollment_id': []}}

    def generate_certificate(self):
        self.ensure_one()

        matricula = self.enrollment_id
        
        if not matricula:
            raise UserError('Matrícula não encontrada ou não selecionada.')

        if matricula.status_do_certificado not in ['FINALIZADO', 'EXPEDIDO', 'EXPEDIDO SEGUNDA VIA']:
            raise UserError('Certificados só podem ser gerados para matrículas com status FINALIZADO, EXPEDIDO ou EXPEDIDO SEGUNDA VIA.')

        _logger.info(f"Status da matrícula antes da atualização: {matricula.status_do_certificado}")

        # Gerar o relatório
        try:
            report_action = self.env.ref(self.template_id.xml_id).report_action(matricula)
        except ValueError:
            raise UserError(f"Ação de relatório não encontrada para o template ID: {self.template_id.xml_id}")
        
        _logger.info(f'Relatório gerado para a matrícula ID: {matricula.id}')
        return report_action


