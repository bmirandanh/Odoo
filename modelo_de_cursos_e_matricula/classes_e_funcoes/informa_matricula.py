from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
import random
from odoo import tools
import logging
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import http
import requests
from odoo.exceptions import UserError
from moodle import Moodle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Frame
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from io import BytesIO
import base64

IS_TEST_ENVIRONMENT = False
_logger = logging.getLogger(__name__)

class InformaMatricula(models.Model):
    """
    Esta classe representa as matrículas dos alunos em cursos.
    """
    _name = 'informa.matricula'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Matriculas'
    _rec_name = 'numero_matricula' 
    
    status_do_certificado = fields.Selection(
        [('CURSANDO','CURSANDO'),
        ('EM FINALIZAÇÃO','EM FINALIZAÇÃO'),
        ('FINALIZADO','FINALIZADO'),
        ('EM PRAZO EXCEDIDO','EM PRAZO EXCEDIDO'),
        ('EXPEDIDO','EXPEDIDO'),
        ('EXPEDIDO SEGUNDA VIA', 'EXPEDIDO SEGUNDA VIA'),
        ('MATRICULA SUSPENSA','MATRICULA SUSPENSA'),
        ], default="CURSANDO", store=True, tracking=True
    )
    matricula_line_ids = fields.One2many(
        'informa.matricula.line', 'matricula_id', string='Disciplinas', readonly=True
    )
    regiao = fields.Selection([
        ('AVA','AVA'),
        ('PRESENCIAL','PRESENCIAL'),
        ] , required=True, tracking=True)
    justificativa_cancelamento = fields.Text(string="Justificativa de Suspensão", tracking=True)
    inscricao_ava = fields.Date(string='Inscrição Ava', required=True, tracking=True)
    email = fields.Char(string="Email", tracking=True)
    telefone = fields.Char(string="Telefone", tracking=True)
    nome_do_aluno = fields.Many2one('res.partner', string="Aluno", required=True, tracking=True, domain=[('aluno', '=', True)])
    curso = fields.Many2one('informa.cursos', string="Curso", required=True, tracking=True)
    prazo_exp_certf_dias = fields.Char(compute='_compute_prazo_exp_certf_dias', string='Prazo exp. Certf. Em dias', tracking=True)
    numero_de_modulo = fields.Char(compute='_compute_numero_de_modulo', tracking=True, string='Nº de Módulo', store=True)
    data_certificacao = fields.Date(string='Data de Certificação')
    data_provavel_certificacao = fields.Date(compute='_compute_data_provavel_certificacao', tracking=True, string='Data provável de certificação', store=True)
    data_original_certificacao = fields.Date(string='Data limite de Certificação', tracking=True, store=True)
    prorrogacao = fields.Boolean(string="Prorrogação", tracking=True)
    data_prorrogacao = fields.Date(string="Data de Prorrogação", tracking=True)
    tipo_de_ingresso = fields.Many2one('tipo.de.ingresso', string="Tipo de ingresso", required=True, tracking=True)
    tipo_de_cancelamento = fields.Many2one('tipo.de.cancelamento', string="Tipo de Suspensão", tracking=True)
    color_tipo_ingresso = fields.Integer(related='tipo_de_ingresso.color', string='Color Index from Tipo de Ingresso')
    color_tipo_cancelamento = fields.Integer(related='tipo_de_cancelamento.color', string='Color Index from Tipo de Suspensão')
    numero_matricula = fields.Char(string="Número de Matrícula", readonly=True)
    matricula_aluno = fields.Char(related='nome_do_aluno.matricula_aluno', string="Matrícula do Aluno", readonly=True)
    cod_curso = fields.Char(compute='_compute_cod_curso', string="Código do Curso", tracking=True, store=True)
    grupo_disciplina_id = fields.Many2one('informa.curriculo', string='Grupo de Disciplina')
    disciplina_ids = fields.Many2many('informa.disciplina', string='Disciplinas')
    disciplina_nomes = fields.Char(compute='_compute_disciplina_nomes')
    last_sequence_sent = fields.Integer(string="Sequência já enviada", default=-1, help="Armazena a sequência do grupo de disciplinas que foi enviada por último.")
    current_sequence = fields.Integer(string="Sequência atual", default=0, help="Armazena a sequência do grupo atual de disciplinas.")
    dias_passados = fields.Integer(string="auxiliar dos dias passados", default=0)
    confirmação_de_dias = fields.Boolean(string="confirmação_de_dias", tracking=False)
    overlapping_disciplines_info = fields.Text(string='Disciplinas Sobrepostas', readonly=True)
    overlapping_disciplines_ids = fields.Many2many('informa.disciplina', 'informa_disciplina_rel', 'disciplina_id', 'overlap_id', string='Disciplinas Sobrepostas', readonly=True)
    overlapping_matricula_ids = fields.Many2many('informa.matricula', 'informa_matricula_rel', 'matricula_id', 'overlap_id', string='Matrículas Sobrepostas', readonly=True)
    overlapping_matricula_descriptions = fields.Char(compute='_compute_overlapping_matriculas', string='Matrículas Sobrepostas', readonly=True)
    allow_grade_editing = fields.Boolean( string="Permitir Edição")
    variant_curriculo_id = fields.Many2one('informa.curriculo.variant', string='Variante do Currículo', domain="[('id', 'in', available_variants)]", store=True)
    total_duracao_horas_id = fields.Float(related='curso.total_duracao_horas', string='Duração(H): ', readonly=True)
    available_variants = fields.Many2many('informa.curriculo.variant', compute='_compute_available_variants')
    moodle = fields.Boolean( string="Moodle?")
    display_name = fields.Char(string='Matrícula (Aluno)', compute='_compute_display_name', store=True)
    disciplina_lines = fields.One2many('informa.registro_disciplina', 'matricula_id', string='Disciplinas')

    @api.depends('nome_do_aluno', 'matricula_aluno')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.matricula_aluno} ({record.nome_do_aluno.name})"

    @api.model
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.matricula_aluno} ({record.nome_do_aluno.name})"
            result.append((record.id, name))
        return result
    
    @staticmethod
    def create_entwined_borders(canvas_obj, width, height):
        # Convertendo width e height para inteiros se eles não forem
        width = int(width)
        height = int(height)

        # Definindo a cor e a largura da linha
        canvas_obj.setStrokeColor(HexColor(0x0000ff))  # Exemplo de cor verde
        canvas_obj.setLineWidth(3)

        # Definindo o tamanho e o espaço entre as bordas
        border_size = 3
        space = 2

        # Desenhando as bordas horizontais superiores e inferiores
        for y in [0, height - border_size]:
            for x in range(0, width, int(border_size + space)):  # Conversão para int aqui
                canvas_obj.line(x, y, x + border_size, y + border_size)
        
        # Desenhando as bordas verticais esquerda e direita
        for x in [0, width - border_size]:
            for y in range(0, height, int(border_size + space)):  # Conversão para int aqui
                canvas_obj.line(x, y, x + border_size, y + border_size)
                
    @staticmethod
    def create_entwined_borders3(canvas_obj, width, height):
        # Convertendo width e height para inteiros se eles não forem
        width = int(width)
        height = int(height)

        # Definindo a cor e a largura da linha
        canvas_obj.setStrokeColor(HexColor(0x0000aa))  # Exemplo de cor azul
        canvas_obj.setLineWidth(3)

        # Definindo o tamanho e o espaço entre as bordas
        border_size = 3
        space = 2

        # Desenhando as bordas horizontais superiores e inferiores
        for y in [0, height - border_size]:
            for x in range(0, width, int(border_size + space)):  # Conversão para int aqui
                canvas_obj.line(x, y, x + border_size, y + border_size)
        
        # Desenhando as bordas verticais esquerda e direita
        for x in [0, width - border_size]:
            for y in range(0, height, int(border_size + space)):  # Conversão para int aqui
                canvas_obj.line(x, y, x + border_size, y + border_size)
                
    @staticmethod
    def create_entwined_borders2(canvas_obj, width, height):
        # Convertendo width e height para inteiros se eles não forem
        width = int(width)
        height = int(height)

        # Definindo a cor e a largura da linha
        canvas_obj.setStrokeColor(HexColor(0x00aa00))  # Exemplo de cor azul
        canvas_obj.setLineWidth(3)

        # Definindo o tamanho e o espaço entre as bordas
        border_size = 3
        space = 2

        # Desenhando as bordas horizontais superiores e inferiores
        for y in [0, height - border_size]:
            for x in range(0, width, int(border_size + space)):  # Conversão para int aqui
                canvas_obj.line(x, y, x + border_size, y + border_size)
        
        # Desenhando as bordas verticais esquerda e direita
        for x in [0, width - border_size]:
            for y in range(0, height, int(border_size + space)):  # Conversão para int aqui
                canvas_obj.line(x, y, x + border_size, y + border_size)    
    
    @api.model
    def generate_certificate(self, numero_matricula):
        # Encontre a matrícula pelo número fornecido
        matricula = self.search([('numero_matricula', '=', numero_matricula)], limit=1)
        if not matricula:
            return {'error': 'Matrícula não encontrada'}

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)
        
        # Estilos
        styles = getSampleStyleSheet()
        aluno_nome = matricula.nome_do_aluno.name
        curso_nome = matricula.curso.name
        tempo_de_conclusao = matricula.total_duracao_horas_id
        data_conclusao = fields.Date.to_string(matricula.data_certificacao)
        
        # Estilos dos parágrafos
        title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=50, alignment=TA_CENTER, spaceAfter=30)
        body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=25, alignment=TA_CENTER, spaceAfter=12, spaceBefore=20)
        detail_style = ParagraphStyle('DetailStyle', parent=styles['BodyText'], fontSize=16, alignment=TA_CENTER, spaceAfter=12, spaceBefore=20)

        # Adição dos elementos
        elements = [
            Paragraph("CERTIFICADO", title_style),
            Spacer(1, 0.8 * inch),
            Paragraph("Certificamos que", body_style),
            Paragraph(f"<b>{aluno_nome}</b>", body_style),
            Spacer(1, 0.8 * inch),
            Paragraph("Concluiu com total aproveitamento o curso:", body_style),
            Paragraph(f"<b>{curso_nome}</b>", body_style),
            Spacer(1, 0.40 * inch),
            Paragraph(f"Com carga horária de {tempo_de_conclusao} horas", detail_style),
            Paragraph(f"Data de conclusão: {data_conclusao}", detail_style)
        ]

        frame = Frame(inch, inch, width - 2 * inch, height - 2 * inch, showBoundary=0)
        frame.addFromList(elements, p)

        # Desenha as bordas entrelaçadas
        self.create_entwined_borders(p, width, height)
        self.create_entwined_borders2(p, width - inch/10, height - inch/10)
        self.create_entwined_borders3(p, width - inch/30, height - inch/30)

        p.showPage()

        # Obtenha registros de disciplina para esta matrícula
        disciplina_records = self.env['informa.matricula.line'].search([('matricula_id', '=', matricula.id)])
        
        title = "Detalhes das Disciplinas Cursadas"
        max_font_size = 18
        min_font_size = 8
        current_font_size = max_font_size
        max_lines_per_page = 200  # Estimativa de linhas que cabem em uma página

        # Ajusta o tamanho da fonte de acordo com a quantidade de disciplinas
        if len(disciplina_records) > max_lines_per_page:
            lines_per_discipline = 2  # Se há muitas disciplinas, cada uma pode ocupar mais de uma linha
            current_font_size = max(min_font_size, int((max_lines_per_page / len(disciplina_records)) * max_font_size))

        # Configuração do título
        p.setFont("Helvetica-Bold", current_font_size)
        p.drawCentredString(width / 2.0, height - inch, title)

        # Configurações iniciais para a lista de disciplinas
        p.setFont("Helvetica", current_font_size)
        current_height = height - 2 * inch  # Começa um pouco abaixo do título
        line_height = 1.2 * current_font_size  # Espaçamento baseado no tamanho da fonte atual

        # Lista as disciplinas na página
        for record in disciplina_records:
            # Se a altura atual for menor que a margem inferior, interrompe o loop
            if current_height < inch * 2:
                break
            
            discipline_text = f" º {record.disciplina_id.name} - Média: {record.media_necessaria} - Nota: {record.nota}"
            p.drawString(inch, current_height, discipline_text)
            current_height -= line_height  # Move para a próxima linha

        # Se não couber na página, informe que as disciplinas adicionais não foram exibidas
        if len(disciplina_records) * line_height > (height - 3 * inch):
            p.drawString(inch, current_height, "Algumas disciplinas não puderam ser exibidas.")
        
        # Criar borda para a segunda página
        self.create_entwined_borders(p, width, height)
            
        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def generate_certificate_button(self):
        """ Função chamada pelo botão para gerar o certificado """
        pdf_data = self.generate_certificate(self.numero_matricula)
        if isinstance(pdf_data, dict) and 'error' in pdf_data:
            raise UserError(pdf_data['error'])
        else:
            # Aqui você pode salvar o PDF em um campo binário ou diretamente enviar para download
            file_name = f"{self.nome_do_aluno.name}_certificado.pdf"
            attachment = self.env['ir.attachment'].create({
                'name': file_name,
                'type': 'binary',
                'datas': base64.b64encode(pdf_data),
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })
            # Você deve usar a URL do anexo para o download
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }   
    
    @api.onchange('curso')
    def _onchange_curso(self):
        # Se um curso for selecionado, carregue as disciplinas associadas a este curso
        for rec in self:
            if rec.curso and rec.curso.variant_curriculo_id:
                rec.variant_curriculo_id = rec.curso.variant_curriculo_id.id
                disciplinas = rec.curso.variant_curriculo_id.disciplina_ids
                # Apagar linhas de matrícula existentes
                rec.matricula_line_ids = [(5, _, _)]
                # Criar novas linhas de matrícula para as disciplinas associadas
                rec.matricula_line_ids = [(0, 0, {
                    'disciplina_id': disciplina.id,
                }) for disciplina in disciplinas]  

    def action_open_menu(self):
        view_id2 = self.env.ref('modelo_de_cursos_e_matricula.view_course_management_form').id
        return {
            'name': 'Menu Principal',
            'type': 'ir.actions.act_window',
            'res_model': 'course.creation.wizard',
            'view_mode': 'form',
            'view_id': view_id2,
            'target': 'new',
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'}
        }
        
    @api.depends('curso')
    def _compute_variant_curriculo_id(self):
        """
        Calcula a variante do currículo com base no curso selecionado.
        """
        for matricula in self:
            matricula.variant_curriculo_id = matricula.curso.variant_curriculo_id
            
    @api.depends('grupo_disciplina_id')
    def _compute_available_variants(self):
        """
        Calcula as variantes disponíveis com base no grupo de disciplinas selecionado.
        """

        for matricula in self:
            matricula.available_variants = matricula.grupo_disciplina_id.variant_ids.ids if matricula.grupo_disciplina_id else []

    @api.onchange('grupo_disciplina_id')
    def _onchange_grupo_disciplina_id(self):
        """
        Atualiza o domínio do campo variant_curriculo_id com base no grupo de disciplinas selecionado.
        """
        if self.grupo_disciplina_id:
            return {'domain': {'variant_curriculo_id': [('id', 'in', self.available_variants)]}}
        else:
            return {'domain': {'variant_curriculo_id': []}}
        
    @api.depends('overlapping_matricula_ids')
    def _compute_overlapping_matriculas(self):
        """
        Calcula as descrições das matrículas sobrepostas.
        """
        for record in self:
            descriptions = record.overlapping_matricula_ids.mapped('numero_matricula')
            record.overlapping_matricula_descriptions = ', '.join(descriptions)
                
    def atualizar_status_dias_passados(self):
        """
        Atualiza o status dos dias passados para todas as matrículas.
        """        
        _logger.info('Atualizar dias passados')
        matriculas = self.search([])  # Isso buscará todos os registros de 'informa.matricula'
        for matricula in matriculas:
            matricula._compute_prazo_exp_certf_dias()

    def get_current_group_sequence(self):
        return self.current_sequence

    @api.depends('status_do_certificado','data_provavel_certificacao','data_original_certificacao', 'inscricao_ava', 'prorrogacao', 'data_prorrogacao', 'dias_passados', 'confirmação_de_dias')
    def _compute_prazo_exp_certf_dias(self):
        dia_de_hoje = date.today()
        for record in self:
            if record.status_do_certificado == 'EXPEDIDO':
                record.prazo_exp_certf_dias = "Expedido"
            elif record.status_do_certificado == 'MATRÍCULA CANCELADA':
                record.prazo_exp_certf_dias = "Matrícula Cancelada"
            elif record.status_do_certificado == 'TRANCADO':
                record.prazo_exp_certf_dias = "Matrícula Trancada"                
            elif record.status_do_certificado == 'FINALIZADO':
                record.prazo_exp_certf_dias = "Curso Finalizado"
            else:
                data_certificacao = record.data_prorrogacao if record.prorrogacao else record.data_original_certificacao
                if record.inscricao_ava and data_certificacao:
                    if record.confirmação_de_dias == False:
                        record.dias_passados = ( record.data_provavel_certificacao - record.inscricao_ava).days - 1
                        _logger.info('data_provavel_certificacao = %s, data_original_certificacao = %s', record.data_provavel_certificacao, record.data_original_certificacao)
                        record.confirmação_de_dias = True
                        _logger.info('confirmação_de_dias de False para True')
                        record.prazo_exp_certf_dias = str(record.dias_passados) + _(" dias")                    
                    elif dia_de_hoje > record.inscricao_ava:
                        diferença_de_dias = ( dia_de_hoje - record.inscricao_ava ).days
                        record.dias_passados = ( record.data_original_certificacao - dia_de_hoje).days
                        _logger.info('Atualizar dias passados - dia_de_hoje > - com date.today()')
                        _logger.info('date.today() = %s', dia_de_hoje)
                        _logger.info('diferença_de_dias = %s', diferença_de_dias)
                        _logger.info('record.data_original_certificacao = %s', record.data_original_certificacao)
                        record.prazo_exp_certf_dias = str(record.dias_passados) + _(" dias")
                    elif dia_de_hoje < record.inscricao_ava:
                        diferença_de_dias = ( record.inscricao_ava - dia_de_hoje ).days
                        record.dias_passados = (record.data_original_certificacao - dia_de_hoje).days
                        _logger.info('Atualizar dias passados - dia_de_hoje < - com date.today()')
                        _logger.info('date.today() = %s', dia_de_hoje)
                        _logger.info('diferença_de_dias = %s', diferença_de_dias)
                        _logger.info('record.data_original_certificacao = %s', record.data_original_certificacao)
                        record.prazo_exp_certf_dias = str(record.dias_passados) + _(" dias")
                    else:
                        record.dias_passados = ( record.data_original_certificacao - dia_de_hoje).days
                        _logger.info('Atualizar dias passados - confirmação_de_dias - com date.today()')
                        _logger.info('date.today() = %s', dia_de_hoje)
                        _logger.info('record.data_original_certificacao = %s', record.data_original_certificacao)
                        record.prazo_exp_certf_dias = str(record.dias_passados) + _(" dias")
                    
                    # Alteração do status baseado no valor de dias_passados
                    if record.dias_passados <= 0:
                        record.status_do_certificado = 'EM PRAZO EXCEDIDO'
                    elif record.dias_passados <= 10:
                        record.status_do_certificado = 'EM FINALIZAÇÃO'
                    else:
                       record.status_do_certificado = 'CURSANDO'
                else:
                    record.prazo_exp_certf_dias = _("Data de provável certificação não definida")
        
    def _connect_moodle(self):
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor         
                
        moodle_url = base_url+"webservice/rest/server.php"
        moodle_token = token
        moodle = Moodle(moodle_url, moodle_token)
        return moodle
    
    def execute_for_all(self):
        _logger.info('Executando método execute_for_all...')
        matricula = self.env['informa.matricula']
        matriculas = self.env['informa.matricula'].search([
            ('status_do_certificado', 'in', ['CURSANDO', 'EM FINALIZAÇÃO', 'EM PRAZO EXCEDIDO'])
        ])
        for matricula in matriculas:
            self.get_released_groups(matricula.id)
        _logger.info('Método execute_for_all concluído.')
        return True        
            
    # Quando os valores dos campos de um registro Disciplina são atualizados, esse método é chamado.
    def write(self, vals):
        _logger.info('Atualizando valores do registro InformaMatricula...')
        status_antigo = self.status_do_certificado
        res = super().write(vals)  # Chamando o método da classe pai corretamente
       # self.update_moodle_information()
        _logger.info('Valores do registro InformaMatricula atualizados.')
        if 'status_do_certificado' in vals and vals['status_do_certificado'] in ['TRANCADO', 'MATRÍCULA CANCELADA'] and status_antigo not in ['TRANCADO', 'MATRÍCULA CANCELADA']:
            # Bloquear o acesso do aluno ao Moodle
            self.block_access_to_moodle()

        # Verifique se o status_do_certificado está sendo alterado para 'FINALIZADO'
        if 'status_do_certificado' in vals and vals['status_do_certificado'] == 'FINALIZADO':
            for record in self:
                # Se o status atual não é 'FINALIZADO', atualize a data_certificacao
                if record.status_do_certificado != 'FINALIZADO':
                    # Defina data_certificacao para a data atual
                    vals['data_certificacao'] = fields.Date.context_today(record)
        return res
    
    def get_moodle_course_id(self, d_data):
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor         
         
        url = base_url+"webservice/rest/server.php"
        
        # Extrair o valor inteiro de d_data
        course_id_value = d_data.get('id')
        if course_id_value is None:
            _logger.error('ID não encontrado em d_data: %s', d_data)
            return None
        
        _logger.info('ID: %s', course_id_value)
        
        params = {
            "wstoken": token,
            "wsfunction": "core_course_get_courses_by_field",
            "field": "idnumber",
            "value": int(course_id_value),  # Converte o valor para inteiro
            "moodlewsrestformat": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()  
        _logger.info('Resposta no Moodle: %s', response.text)

        if 'courses' in data and len(data['courses']) > 0:
            return data['courses'][0]['id']
        else:
            return None
        
    def get_moodle_course_id_int(self, course_id_value):
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor        
         
        url = base_url+"webservice/rest/server.php"
        
        if course_id_value is None:
            _logger.error('ID do curso não fornecido')
            return None
        
        _logger.info('ID do curso: %s', course_id_value)
        
        params = {
            "wstoken": token,
            "wsfunction": "core_course_get_courses_by_field",
            "field": "idnumber",
            "value": course_id_value,
            "moodlewsrestformat": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()  
        _logger.info('Resposta no Moodle: %s', response.text)

        if 'courses' in data and len(data['courses']) > 0:
            return data['courses'][0]['id']
        else:
            return None
            
    def get_moodle_user_id(self, user_id):
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor        
        
        url = base_url+"webservice/rest/server.php"
        _logger.info('user_id: %s', user_id)
        params = {
            "wstoken": token,
            "wsfunction": "core_user_get_users_by_field",
            "field": "idnumber",
            "values[0]": user_id,
            "moodlewsrestformat": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()
        _logger.info('Resposta no Moodle: %s', response.text)
        
        if data and len(data) > 0:
            return data[0]['id']
        else:
            return None
    
    ##### Aqui inicia os métodos de atualização da Cron, em questão a vinculação das disciplinas para os alunos
     
    def enrol_user_to_course(self, user_id, course_id):
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor
        
        # URL base para o serviço web do Moodle
        MOODLE_URL = base_url+"webservice/rest/server.php"
        
        # Parâmetros para a requisição
        params = {
            "wstoken": token,
            "wsfunction": "enrol_manual_enrol_users",
            "moodlewsrestformat": "json",
            "enrolments[0][roleid]": 5,
            "enrolments[0][userid]": user_id,
            "enrolments[0][courseid]": course_id
        }
        
        # Fazendo a requisição POST
        response = requests.post(MOODLE_URL, params=params)
            
        if response.status_code == 200:
            _logger.error('Resposta no Moodle: %s', response.text)
            return response.json()
        else:
            _logger.error('Erro ao inscrever usuário no curso no Moodle: %s', response.text)
            raise UserError(_('Erro ao inscrever usuário no curso no Moodle! Houve algum problema na inscrição.'))

    def block_access_to_moodle(self, moodle_aluno_id, moodle_curso_id):
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url = base_url_param.valor
        token = token_param.valor
        
        moodle_url = base_url+"webservice/rest/server.php"
        user_id = moodle_aluno_id
        course_id = moodle_curso_id
        
        if user_id and course_id:
            params = {
                "wstoken": token,
                "wsfunction": "enrol_manual_unenrol_users",
                "moodlewsrestformat": "json",
                "enrolments[0][userid]": user_id,
                "enrolments[0][courseid]": course_id,
                "enrolments[0][roleid]": 5,
            }
            response = requests.post(moodle_url, params=params)
            if response.status_code == 200:
                _logger.info('Usuário suspenso no Moodle: %s', response.text)
            else:
                _logger.error('Erro ao suspender usuário no Moodle: %s', response.text)
                
    def has_no_grade_as_dash(self, course_id, user_id):
        
        # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
        ParamObj = self.env['fgmed.config.params']
        
        # Buscando as configurações de base_url e token
        base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
        token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

        # Atribuindo os valores encontrados ou definindo um valor padrão
        base_url_m = base_url_param.valor
        token = token_param.valor             
        
        url = "https://avadev.medflix.club/webservice/rest/server.php"
        params = {
            "wstoken": "c502156af2c00a4b3e9e5d878922be46",
            "wsfunction": "gradereport_user_get_grade_items",
            "courseid": course_id,
            "userid": user_id,
            "moodlewsrestformat": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()

        if 'usergrades' in data:
            for grade_item in data['usergrades'][0]['gradeitems']:
                if grade_item['gradeformatted'] == "-":
                    return True
        return False
                        
    def check_approved_disciplinas(self):
        registro_disciplinas = self.env['informa.registro_disciplina'].search([('status', '=', 'aprovado')])
        for registro in registro_disciplinas:
            curso_id = registro.curso_id.id
            aluno_id = registro.aluno_id.id
            moodle_curso_id = self.get_moodle_course_id_int(curso_id)
            moodle_aluno_id = self.get_moodle_user_id(aluno_id)
            if moodle_curso_id and moodle_aluno_id and not self.has_no_grade_as_dash(moodle_curso_id, moodle_aluno_id):
                self.block_access_to_moodle(moodle_aluno_id, moodle_curso_id)

    def check_reproved_disciplinas(self):
        registro_disciplinas = self.env['informa.registro_disciplina'].search([('status', '=', 'reprovado')])
        for registro in registro_disciplinas:
            curso_id = registro.curso_id.id
            aluno_id = registro.aluno_id.id
            moodle_curso_id = self.get_moodle_course_id_int(curso_id)
            moodle_aluno_id = self.get_moodle_user_id(aluno_id)
            if moodle_curso_id and moodle_aluno_id and not self.has_no_grade_as_dash(moodle_curso_id, moodle_aluno_id):
                self.block_access_to_moodle(moodle_aluno_id, moodle_curso_id)
    
    def get_released_groups(self, matricula_id):
        matricula = self.env['informa.matricula'].browse(matricula_id)
        _logger.info('Obtendo grupos liberados para a matrícula ID %d...', matricula_id)

        if not matricula:
            return {'error': 'Matrícula não encontrada.'}

        aluno_name = matricula.nome_do_aluno.name
        _logger.info('Matrícula pertence ao aluno %s.', aluno_name)

        curso = matricula.curso
        if not curso:
            return {'error': 'Curso não associado à matrícula.'}

        grupos = curso.variant_curriculo_id.sorted(key=lambda g: g.sequence)
        current_sequence = matricula.current_sequence
        user_id = matricula.nome_do_aluno.id
        _logger.info('user_id = %s.', user_id)

        # Trata o caso especial da sequência 0
        _logger.info('current_sequence = %s.', matricula.current_sequence)
        if matricula.current_sequence == 0:
            if grupos[current_sequence].days_to_release <= 0:
                disciplinas_data = [{
                    'id': disciplina.id,
                } for disciplina in grupos[current_sequence].disciplina_ids]
                _logger.info('disciplinas_data = %s.', disciplinas_data)
                todas_disciplinas_enviadas = True
                for d_data in disciplinas_data:
                    moodle_course_id = self.get_moodle_course_id(d_data)
                    _logger.info('d_data = %s', d_data)
                    _logger.info('moodle_course_id = %s', moodle_course_id)
                    moodle_user_id = self.get_moodle_user_id(user_id)
                    _logger.info('moodle_user_id = %s', moodle_user_id)
                    if moodle_course_id and moodle_user_id:
                        _logger.info('Enviando para %s, o id de curso = %s.', moodle_user_id, moodle_course_id)
                        self.enrol_user_to_course(user_id=moodle_user_id, course_id=moodle_course_id)
                    else:
                        todas_disciplinas_enviadas = False
                        _logger.info('Erro ao enviar disciplina ID %s para o usuário ID %s.', d_data['id'], user_id)
            if todas_disciplinas_enviadas:
                matricula.current_sequence += 1
                _logger.info(' aumento de sequência para = %s ', matricula.current_sequence)
            else:
                _logger.info(' Ainda não é tempo de liberar a sequência 0 ')
                

        # Tratando sequências posteriores
        else:
            disciplinas_anteriores = grupos[current_sequence-1].disciplina_ids
            _logger.info('disciplinas_anteriores = %s.', disciplinas_anteriores)
            registros_disciplinas = self.env['informa.registro_disciplina'].search([
                ('matricula_id', '=', matricula.id),
                ('disciplina_id', 'in', disciplinas_anteriores.ids)
            ])
            if all(record.status == 'aprovado' for record in registros_disciplinas):
                if grupos[current_sequence].days_to_release <= 0:
                    disciplinas_data = [{
                        'id': disciplina.id,
                    } for disciplina in grupos[current_sequence].disciplina_ids]
                    _logger.info('disciplinas_data = %s.', disciplinas_data)
                    todas_disciplinas_enviadas = True
                    for d_data in disciplinas_data:
                        moodle_course_id = self.get_moodle_course_id(d_data)
                        _logger.info('moodle_course_id = %s', moodle_course_id)
                        moodle_user_id = self.get_moodle_user_id(user_id)
                        _logger.info('moodle_user_id = %s', moodle_user_id)
                        if moodle_course_id and moodle_user_id:
                            _logger.info('Enviando para %s, o id de curso = %s.', moodle_user_id, moodle_course_id)
                            matricula.last_sequence_sent = matricula.current_sequence
                            _logger.info('current_sequence = %s.', matricula.current_sequence)
                            self.enrol_user_to_course(user_id=moodle_user_id, course_id=moodle_course_id)
                        else:
                            todas_disciplinas_enviadas = False
                            _logger.info('Erro no GET de get_moodle_course_id.')
                            _logger.info('Erro ao enviar disciplina ID %s para o usuário ID %s.', d_data['id'], user_id)
                if todas_disciplinas_enviadas:
                    matricula.current_sequence += 1
                    _logger.info(' aumento de sequência para = %s ', matricula.current_sequence)
                else:
                    _logger.info('Ainda não é tempo de liberar a sequência atual.')
            else:
                _logger.info(' O aluno ainda não passou em todas as disciplinas da sequência anterior.')

        return {'message': 'Cron concluída.'}
        # Fim dos métodos de atualização da Cron para vinculação das disciplinas aos alunos
    
    # métodos de update de informações para o moodle    
    def update_moodle_information(self):
        """
        Envia informações atualizadas da matrícula para o Moodle.
        """
        if not self.moodle:
            return {'success': False, 'message': 'Integração com Moodle desativada.'}
        
        for matricula in self:
            aluno_name = matricula.nome_do_aluno.name
            curso_name = matricula.curso.name if matricula.curso else ''
            email = matricula.email
            telefone = matricula.telefone
            
            data_to_send = {
                'matricula_id': matricula.id,
                'aluno_name': aluno_name,
                'curso_name': curso_name,
                'email': email,
                'telefone': telefone
            }
            
            if IS_TEST_ENVIRONMENT:
                _logger.info('Envio simulado para o Moodle. Informações da Matrícula: %s', data_to_send)
                return {
                    'message': 'Envio realizado (simulado)',
                    'data': data_to_send
                }
            moodle = self._connect_moodle()
            # O método para atualizar informações da matrícula seja 'custom_method_update_matricula'
            response = moodle('custom_method_update_matricula', data_to_send)
            
            # Suponha que a resposta seja um dicionário e tenha uma chave 'success'
            if not response.get('success'):
                _logger.error('Erro ao enviar dados para o Moodle.')
        return True

    def custom_method_update_matricula(self, data):
        """
        Método para atualizar as informações do aluno no Moodle.

        :param data: Um dicionário contendo as informações do aluno que precisam ser atualizadas.
        :return: Um dicionário contendo informações sobre o sucesso ou falha da operação.
        """
        if not self.moodle:
            return {'success': False, 'message': 'Integração com Moodle desativada.'}
        
        moodlec = self._connect_moodle()
        # Primeiro, tente obter o ID do aluno no Moodle usando o nome (ou outra identificação única, como e-mail ou matrícula).
        try:
            response = moodlec.call('core_user_get_users', {'criteria': [{'key': 'username', 'value': data['aluno_name']}]})
            if not response:
                return {'success': False, 'message': "Aluno não encontrado no Moodle."}
            user_id = response[0]['id']
        except Exception as e:
            return {'success': False, 'message': f"Erro ao buscar aluno no Moodle: {e}"}
        # Atualizar as informações do aluno.
        # Presumindo que o Moodle tenha uma função chamada 'core_user_update_users' para atualizar informações do usuário.
        users_data = [{
            'id': user_id,
            'firstname': data.get('firstname', ''),
            'lastname': data.get('lastname', ''),
            'email': data.get('email', ''),
        }]
        try:
            moodlec.call('core_user_update_users', users_data)
            return {'success': True, 'message': "Informações do aluno atualizadas com sucesso."}
        except Exception as e:
            return {'success': False, 'message': f"Erro ao atualizar informações do aluno: {e}"}   

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
        
    def reingressar_matricula_wizard(self):
        self.ensure_one()  # Garante que apenas um registro é selecionado
        view_id = self.env.ref('modelo_de_cursos_e_matricula.view_matricula_reingresso_wizard_form').id
        return {
            'name': 'Re-ingressar Matrícula',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'matricula.reingresso.wizard',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_matricula_id': self.id}
        }
        
    @api.depends('disciplina_ids')
    def _compute_disciplina_nomes(self):
        for record in self:
            names = ", ".join(record.disciplina_ids.mapped('name'))
            record.disciplina_nomes = names
    
    def atualizar_status_matricula(self):
        for matricula in self:
            registros_disciplina = self.env['informa.registro_disciplina'].search([('matricula_id', '=', matricula.id)])
            if registros_disciplina and all(record.status == 'aprovado' for record in registros_disciplina):
                matricula.status_do_certificado = 'FINALIZADO'

    
    def _update_related_disciplinas(self):
        for matricula in self:
            disciplinas = self.env['informa.registro_disciplina'].search([('matricula_id', '=', matricula.id)]).mapped('disciplina_id')
            matricula.disciplina_ids = [(6, 0, disciplinas.ids)]
    
    @api.model
    def create(self, vals):
        # Verificações iniciais e preparações de dados
        aluno_id = vals.get('nome_do_aluno')
        curso_id = vals.get('curso')

        # Checa se já existe matrícula para o aluno no curso
        if self.search([('nome_do_aluno', '=', aluno_id), ('curso', '=', curso_id)]):
            raise UserError(_('O aluno já possui uma matrícula neste curso!'))

        # Prepara as disciplinas para a linha de matrícula baseada na variante do currículo selecionado
        disciplina_ids = vals.pop('disciplina_ids', False)
        if disciplina_ids and disciplina_ids[0][0] == 6:
            vals['matricula_line_ids'] = [(0, 0, {'disciplina_id': d_id}) for d_id in disciplina_ids[0][2]]

        # Cria o registro da matrícula
        matricula_record = super(InformaMatricula, self).create(vals)
        
        # Lógica para registrar a criação na auditoria
        self.env['audit.log.report'].create_log(matricula_record, vals, action='create')
        
        # Verificar se o aluno tem matrícula em algum curso que contém disciplinas iguais.
        all_matriculas = self.search([('nome_do_aluno', '=', aluno_id)])
        
        # Corrigindo a obtenção das disciplinas
        new_disciplinas_from_groups = self.env['informa.cursos'].browse(curso_id).variant_curriculo_id.mapped('disciplina_ids')
        
        overlapping_courses = []
        for matricula in all_matriculas - matricula_record:
            common_disciplinas = new_disciplinas_from_groups & matricula.curso.variant_curriculo_id.mapped('disciplina_ids')
            if common_disciplinas:
                for disciplina in common_disciplinas:
                    overlapping_courses.append((disciplina.id, disciplina.name, matricula.id, matricula.numero_matricula))
                    
        if overlapping_courses:
            overlapping_disciplinas = [item[0] for item in overlapping_courses]
            overlapping_matriculas = [item[2] for item in overlapping_courses]
            matricula_record.write({
                'overlapping_disciplines_ids': [(6, 0, overlapping_disciplinas)],
                'overlapping_matricula_ids': [(6, 0, overlapping_matriculas)],
            })
            
        # Pegue as disciplinas permitidas para o curso associado à matrícula.
        allowed_disciplinas = self.compute_allowed_disciplinas(matricula_record.curso)
        
        # Para cada disciplina permitida, crie um novo registro de 'RegistroDisciplina'.
        for disciplina in allowed_disciplinas:
            if disciplina.id:
                self.env['informa.registro_disciplina'].create({
                    'aluno_id': matricula_record.nome_do_aluno.id,
                    'curso_id': matricula_record.curso.id,
                    'matricula_id': matricula_record.id,
                    'disciplina_id': disciplina.id,
                })
                
        if not self._context.get('skip_status_update'):
            matricula_record.with_context(skip_status_update=True).atualizar_status_matricula()
            
        # Método para levar as informações para o moodle 
        if self.moodle:
            self._register_student_in_moodle(matricula_record)

    # Ajusta datas se necessário
        if 'data_provavel_certificacao' in vals and 'data_original_certificacao' not in vals:
            matricula_record.data_original_certificacao = vals['data_provavel_certificacao']
            
        if vals.get('status_do_certificado') == 'FINALIZADO':
            matricula_record.data_certificacao = fields.Date.context_today(self)
            
        # Verifica se o curso associado tem um curriculo e disciplinas associadas
        if matricula_record.curso and matricula_record.curso.variant_curriculo_id:
            disciplinas = matricula_record.curso.variant_curriculo_id.disciplina_ids
            # Criar novas linhas de matrícula para as disciplinas associadas
            linhas_disciplina = [(0, 0, {
                'disciplina_id': disciplina.id,
            }) for disciplina in disciplinas]
            matricula_record.write({'matricula_line_ids': linhas_disciplina})
            
        return matricula_record

    def write(self, vals):
        result = super(InformaMatricula, self).write(vals)

        # Lógica para registrar a atualização na auditoria
        for record in self:
            self.env['audit.log.report'].create_log(record, vals, action='write')
        
        # Se algum dos campos de interesse foi alterado, envie atualizações para o Moodle
        fields_of_interest = ['email', 'telefone', 'nome_do_aluno', 'curso']
        if self.moodle:
            if any(field in vals for field in fields_of_interest):
                self.update_moodle_information()

        if not self._context.get('skip_status_update'):
            self.with_context(skip_status_update=True).atualizar_status_matricula()
        
        for record in self.filtered(lambda r: r.status_do_certificado == 'FINALIZADO' and not r.data_certificacao):
            record.data_certificacao = fields.Date.context_today(record)
            super(InformaMatricula, record).write({'data_certificacao': record.data_certificacao})
                    
        return result

    def unlink(self):
        # Preparar dados para o log de auditoria antes da exclusão
        for record in self:
            log_vals = {
                'model_name': record._name,
                'action': 'unlink',
                'field_name': '',
                'old_value': '',
                'new_value': f'Registro Excluído com ID {record.id}',
                'user_id': self.env.user.id,
                'change_date': fields.Datetime.now(),
            }
            self.env['audit.log.report'].create(log_vals)

        # Chamar o método original de 'unlink'
        return super(InformaMatricula, self).unlink()  

    def _register_student_in_moodle(self, matricula):
        
        if self.moodle:    
            # Obtendo acesso ao modelo de configurações do módulo fgmed_config_params
            ParamObj = self.env['fgmed.config.params']
            
            # Buscando as configurações de base_url e token
            base_url_param = ParamObj.search([('chave', '=', 'moodle_base_url')], limit=1)
            token_param = ParamObj.search([('chave', '=', 'moodle_token')], limit=1)

            # Atribuindo os valores encontrados ou definindo um valor padrão
            base_url_m = base_url_param.valor
            token_m = token_param.valor         
                            
            base_url = base_url_m+"webservice/rest/server.php"
            token = token_m
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Divida o nome completo no primeiro espaço
            names = matricula.nome_do_aluno.name.split(' ', 1)
            firstname = names[0]
            lastname = names[1] if len(names) > 1 else firstname
            matricula_id = matricula.nome_do_aluno.id
            # Assegure que a variável 'cpf' seja definida antes de ser usada
            cpf = matricula.nome_do_aluno.l10n_br_cnpj_cpf
            cpfform = 'Fg@' + cpf
                
            # Obtenha os objetos de modelo necessários
            AuthUserObj = self.env['custom.auth.user']
            PartnerObj = self.env['res.partner']

            # Verifique se o usuário já existe no modelo custom.auth.user
            existing_auth_user = AuthUserObj.search([('username', '=', cpf)], limit=1)

            # Se o usuário não existir no modelo custom.auth.user, crie um novo
            if not existing_auth_user:
                # A partir da matrícula, obtenha o partner_id
                partner_id = PartnerObj.search([('id', '=', matricula.nome_do_aluno.id)], limit=1)

                # Crie um novo usuário no modelo custom.auth.user
                if partner_id:
                    new_auth_user = AuthUserObj.create({
                        'username': cpf,
                        'password': cpfform,  # Ou qualquer lógica para definir a senha aqui
                        'partner_id': partner_id.id,
                        # 'image': 'Sua lógica para definir a imagem, se necessário'
                    })
                    _logger.info('Novo usuário de autenticação customizada criado: %s', new_auth_user.username)
                else:
                    raise UserError(_('Parceiro não encontrado para a matrícula fornecida!'))        

            if IS_TEST_ENVIRONMENT:
                # Se estivermos em um ambiente de teste, simplesmente logue a simulação e retorne.
                _logger.info('Envio simulado para o Moodle. Nome do aluno: %s, CPF: %s', matricula.nome_do_aluno.name, cpf)
                return {
                    'message': 'Envio realizado (simulado)',
                    'data': {
                        "username": cpf,
                        "firstname": firstname,
                        "lastname": lastname,
                        "auth": "auth_fgmed",
                        "email": matricula.email
                    }
                }

            # Primeiro, verifique se o usuário já existe
            user_check_url = f"{base_url}/webservice/rest/server.php?wstoken={token}&wsfunction=core_user_get_users_by_field&field=username&values[0]={cpf}&moodlewsrestformat=json"
            response = requests.get(user_check_url, headers=headers)
            
            # Ajuste a maneira como você extrai a resposta
            users = response.json()

            if len(users) == 0:  # Se a lista estiver vazia, o usuário não existe
                # Construir os dados para a criação do usuário
                user_data = {
                    "users[0][username]": cpf,
                    "users[0][password]": cpfform,
                    "users[0][firstname]": firstname,
                    "users[0][lastname]": lastname,
                    "users[0][email]": matricula.email,
                    "users[0][idnumber]":matricula_id,
                    "users[0][auth]": "auth_fgmed",
                }
            
                # Se o usuário não existir, criamos um novo
                signup_url = f"{base_url}webservice/rest/server.php?wstoken={token}&wsfunction=core_user_create_users&moodlewsrestformat=json"
                for key, value in user_data.items():
                    signup_url += f"&{key}={value}"

                response = requests.get(signup_url, headers=headers)  # Usamos GET aqui
                _logger.info('Resposta do Moodle ao criar usuário: %s', response.text)
                if response.status_code != 200:
                    _logger.error('Erro ao criar usuário no Moodle: %s', response.text)
                    raise UserError(_('Erro ao criar usuário no Moodle! O usuário já existe ou houve algum problema na criação.'))
            else:
                _logger.info('No Moodle O usuário já existe.')
                pass
        
    def compute_allowed_disciplinas(self, curso_id):
        # Buscar todas as disciplinas associadas aos grupos de disciplinas do curso selecionado
        disciplinas = self.env['informa.disciplina']
        for grupo in curso_id.variant_curriculo_id:
            disciplinas |= grupo.disciplina_ids
        return disciplinas
                
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
    
    @api.depends('numero_de_modulo', 'inscricao_ava', 'prorrogacao', 'data_prorrogacao')
    def _compute_data_provavel_certificacao(self):
        for record in self:
            if record.inscricao_ava:
                # Considerar prorrogação
                if record.prorrogacao and record.data_prorrogacao:
                    record.data_original_certificacao = record.data_prorrogacao
                    continue
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
                    
                # Atualizar data_original_certificacao aqui
                record.data_original_certificacao = record.data_provavel_certificacao
            else:
                record.data_provavel_certificacao = False

    @api.depends('curso.tempo_de_conclusao')
    def _compute_numero_de_modulo(self):
        for record in self:
            record.numero_de_modulo = record.curso.tempo_de_conclusao or False

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
    