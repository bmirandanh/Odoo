from odoo import models, fields, api
from odoo.exceptions import UserError
from io import BytesIO
from PyPDF2 import PdfFileWriter, PdfFileReader
import logging

_logger = logging.getLogger(__name__)

class InformaCertificado(models.TransientModel):
    _name = 'informa.certificado'
    _description = 'Certificate Wizard'

    student_id = fields.Many2one('res.partner', string='Aluno', required=True)
    enrollment_id = fields.Many2one('informa.matricula', string='Matrícula', required=True)
    template_page1_id = fields.Many2one('ir.ui.view', string='Template Página 1', domain="[('type', '=', 'qweb')]")
    template_page2_id = fields.Many2one('ir.ui.view', string='Template Página 2', domain="[('type', '=', 'qweb')]")

    @api.onchange('student_id')
    def _onchange_student_id(self):
        self.enrollment_id = False
        if self.student_id:
            return {'domain': {'enrollment_id': [('nome_do_aluno', '=', self.student_id.id), ('status_do_certificado', '=', 'FINALIZADO')]}}

    def generate_certificate(self):
        matricula = self.enrollment_id
        if not matricula or matricula.status_do_certificado != 'FINALIZADO':
            raise UserError('Certificados só podem ser gerados para matrículas com status FINALIZADO.')

        # Verificar o status da matrícula
        if matricula.status_do_certificado not in ['FINALIZADO', 'EXPEDIDO', 'EXPEDIDO SEGUNDA VIA']:
            raise UserError('Certificados só podem ser gerados para matrículas com status FINALIZADO, EXPEDIDO ou EXPEDIDO SEGUNDA VIA.')

        # Dados para os templates
        aluno_nome = matricula.nome_do_aluno.name if matricula.nome_do_aluno else 'Nome não encontrado'
        curso_nome = matricula.curso.name if matricula.curso else 'Curso não encontrado'
        tempo_de_conclusao = matricula.total_duracao_horas_id
        data_conclusao = matricula.data_certificacao.strftime('%d/%m/%Y') if matricula.data_certificacao else 'Data não encontrada'

        data = {
            'aluno_nome': aluno_nome,
            'curso_nome': curso_nome,
            'tempo_de_conclusao': tempo_de_conclusao,
            'data_conclusao': data_conclusao,
            'disciplina_records': self.env['informa.matricula.line'].sudo().search([('matricula_id', '=', matricula.id)])
        }

        # Buscar os templates pelo ID
        template_id_page1 = self.template_page1_id
        template_id_page2 = self.template_page2_id
        
        if not template_id_page1.exists():
            raise UserError(f'Template {self.template_page1_id.id} não encontrado')
        if not template_id_page2.exists():
            raise UserError(f'Template {self.template_page2_id.id} não encontrado')

        try:
            # Renderizar o PDF da primeira página usando o template fornecido
            Report = self.env['ir.actions.report']
            pdf_page1_content, _ = Report._render_qweb_pdf(template_id_page1.id, [matricula.id])

            # Renderizar o PDF da segunda página usando o template fornecido
            pdf_page2_content, _ = Report._render_qweb_pdf(template_id_page2.id, [matricula.id])

            # Combine os PDFs da primeira e segunda página
            output_pdf = PdfFileWriter()
            input_pdf_1st_page = PdfFileReader(BytesIO(pdf_page1_content))
            input_pdf_2nd_page = PdfFileReader(BytesIO(pdf_page2_content))

            output_pdf.addPage(input_pdf_1st_page.getPage(0))
            output_pdf.addPage(input_pdf_2nd_page.getPage(0))

            final_output = BytesIO()
            output_pdf.write(final_output)
            final_output.seek(0)

            # Atualizar o status da matrícula
            if matricula.status_do_certificado == 'FINALIZADO':
                matricula.status_do_certificado = 'EXPEDIDO'
            elif matricula.status_do_certificado == 'EXPEDIDO':
                matricula.status_do_certificado = 'EXPEDIDO SEGUNDA VIA'

            # Download do certificado
            return {
                'type': 'ir.actions.act_url',
                'url': f'data:application/pdf;base64,{final_output.getvalue().encode("base64")}',
                'target': 'new',
            }
        except Exception as e:
            _logger.error(f'Erro ao gerar certificado: {str(e)}')
            raise UserError(f'Erro ao gerar certificado: {str(e)}')
