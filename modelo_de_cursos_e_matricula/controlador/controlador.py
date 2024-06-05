from odoo import http
from odoo.http import request, Response
import json
import random
from datetime import date, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import Frame, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime, timedelta

class CertificateController(http.Controller):
        
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

    @http.route('/api/generate_certificate/<string:numero_matricula>', auth='none', type='http', methods=['GET'])
    def generate_certificate(self, numero_matricula, **kw):
        # Encontre a matrícula pelo número fornecido
        matricula = request.env['informa.matricula'].sudo().search([('numero_matricula', '=', numero_matricula)], limit=1)
        if not matricula:
            return json.dumps({'error': 'Matrícula não encontrada'})

        buffer = BytesIO()
        # Aqui mudamos para landscape para alterar a orientação da página
        p = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)
        
        # Estilos
        styles = getSampleStyleSheet()
        aluno_nome = matricula.nome_do_aluno.name if matricula.nome_do_aluno else 'Nome não encontrado'
        curso_nome = matricula.curso.name if matricula.curso else 'Curso não encontrado'
        tempo_de_conclusao = matricula.total_duracao_horas_id
        data_conclusao = matricula.data_certificacao.strftime('%d/%m/%Y')
        
        # Estilos dos parágrafos
        title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=50, alignment=TA_CENTER, spaceAfter=30)
        body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=25, alignment=TA_CENTER, spaceAfter=12, spaceBefore=20)
        detail_style = ParagraphStyle('DetailStyle', parent=styles['BodyText'], fontSize=16, alignment=TA_CENTER, spaceAfter=12, spaceBefore=20)

        # Adição dos elementos
        elements = [
            Paragraph("CERTIFICADO", title_style),
            Spacer(1, 0.8 * inch),
            Paragraph(f"Certificamos que", body_style),
            Paragraph(f"<b>{aluno_nome}</b>", body_style),
            Spacer(1, 0.8 * inch),
            Paragraph(f"Concluiu com total aproveitamento o curso:", body_style),
            Paragraph(f"<b>{curso_nome}</b>", body_style),
            Spacer(1, 0.40 * inch),
            Paragraph(f"Com carga horária de {tempo_de_conclusao} horas", detail_style),
            Paragraph(f"Data de conclusão: {data_conclusao}", detail_style)
        ]
        
        # Desenha as bordas entrelaçadas           
        CertificateController.create_entwined_borders(p, width, height)
        CertificateController.create_entwined_borders2(p, width - inch/10, height - inch/10)
        CertificateController.create_entwined_borders3(p, width - inch/30, height - inch/30)

        # Centralização vertical dos elementos
        frame = Frame(inch, inch, width - 2 * inch, height - 2 * inch, showBoundary=0)
        frame.addFromList(elements, p)
        
        # Finaliza a primeira página e inicia a segunda página
        p.showPage()

        # Obtenha registros de disciplina para esta matrícula
        disciplina_records = request.env['informa.matricula.line'].sudo().search([('matricula_id', '=', matricula.id)])

        # Defina o título para a segunda página
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
        CertificateController.create_entwined_borders(p, width, height)
            
        # Finaliza a segunda página
        p.showPage()
        
        # Finaliza o PDF e obtém os dados
        p.save()
        pdf = buffer.getvalue()
        buffer.close()

        # Configura os cabeçalhos da resposta e retorna o PDF
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', f'attachment; filename="{matricula.nome_do_aluno.name}_certificado.pdf"')
        ]
        return request.make_response(pdf, headers=headers)        
    
    
class DisciplinaController(http.Controller):

    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True

    @http.route('/api/disciplina/all', auth='none', type='http', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def get_all_disciplinas(self, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*', 
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            response = request.make_response(json.dumps({'error': 'invalid token'}), headers=headers)
            response.status_code = 401
            return response

        try:
            disciplinas = request.env['informa.disciplina'].sudo().search_read([], ['name', 'media', 'grupo_disciplina_id', 'cod_disciplina'])
            response = request.make_response(json.dumps({'success': True, 'disciplinas': disciplinas}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response


    @http.route('/api/disciplina/<string:cod_disciplina>', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_disciplina_by_cod(self, cod_disciplina, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            response = request.make_response(json.dumps({'error': 'invalid token'}), headers=headers)
            response.status_code = 401
            return response

        try:
            disciplina = request.env['informa.disciplina'].sudo().search([('cod_disciplina', '=', cod_disciplina)], limit=1)
            if not disciplina:
                response = request.make_response(json.dumps({'error': 'Disciplina not found'}), headers=headers)
                response.status_code = 404
                return response

            disciplina_data = {
                'name': disciplina.name,
                'media': disciplina.media,
                'grupo_disciplina_id': disciplina.grupo_disciplina_id.id if disciplina.grupo_disciplina_id else None,
                'cod_disciplina': disciplina.cod_disciplina,
            }
            response = request.make_response(json.dumps({'success': True, 'disciplina': disciplina_data}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response
        
    @http.route('/api/disciplina/create', auth='none', type='json', methods=['POST', 'OPTIONS'], cors='*')
    def create_disciplina(self, **kw):

        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        data = request.jsonrequest
        try:
            new_disciplina = request.env['informa.disciplina'].sudo().create({
                'name': data.get('name'),
                'media': data.get('media'),
                'professor': data.get('professor'),
                'duracao_horas': data.get('duracao_horas'),
                'cod_disciplina': data.get('cod_disciplina'),
            })
            return {'success': True, 'id': new_disciplina.id}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/disciplina/delete/<string:cod_disciplina>', auth='none', type='http', methods=['DELETE', 'OPTIONS'], csrf=False, cors='*')
    def delete_disciplina(self, cod_disciplina, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            response = request.make_response(json.dumps({'error': 'invalid token'}), headers=headers)
            response.status_code = 401
            return response
        disciplina = request.env['informa.disciplina'].sudo().search([('cod_disciplina', '=', cod_disciplina)], limit=1)
        if not disciplina:
            response = request.make_response(json.dumps({'error': 'Disciplina not found'}), headers=headers)
            response.status_code = 404
            return response
        
        try:
            disciplina.unlink()
            response = request.make_response(json.dumps({'success': True}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response

    @http.route(['/api/disciplina/update/<string:cod_disciplina>', '/api/disciplina/update/<string:cod_disciplina>/<attribute>'], auth='none', type='json', methods=['PUT', 'OPTIONS'], csrf=False, cors='*')
    def update_disciplina(self, cod_disciplina, attribute=None, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            response = request.make_response(json.dumps({'error': 'invalid token'}), headers=headers)
            response.status_code = 401
            return response

        disciplina = request.env['informa.disciplina'].sudo().search([('cod_disciplina', '=', cod_disciplina)], limit=1)
        if not disciplina:
            response = request.make_response(json.dumps({'error': 'Disciplina not found'}), headers=headers)
            response.status_code = 404
            return response

        data = json.loads(request.httprequest.data)
        update_vals = {}
        if attribute:
            if attribute in ['name', 'media', 'cod_disciplina'] and attribute in data:
                update_vals[attribute] = data[attribute]
            else:
                response = request.make_response(json.dumps({'error': 'Invalid attribute or missing data'}), headers=headers)
                response.status_code = 400
                return response
        else:
            for attr in ['name', 'media', 'cod_disciplina']:
                if attr in data:
                    update_vals[attr] = data[attr]

        try:
            disciplina.write(update_vals)
            response = request.make_response(json.dumps({'success': True}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response

class TipoIngressoController(http.Controller):

    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True
    
    @http.route('/api/tipoingresso/all', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_all_tipoingresso(self, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            response = request.make_response(json.dumps({'error': 'invalid token'}), headers=headers)
            response.status_code = 401
            return response

        try:
            tipo_ingresso = request.env['tipo.de.ingresso'].sudo().search_read([], ['nome', 'descricao', 'color', 'cod_ingresso'])
            response = request.make_response(json.dumps({'success': True, 'tipos de ingresso': tipo_ingresso}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response

    @http.route('/api/tipoingresso/<string:cod_ingresso>', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_tipoingresso_by_cod(self, cod_ingresso, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            response = request.make_response(json.dumps({'error': 'invalid token'}), headers=headers)
            response.status_code = 401
            return response

        tipo_ingresso = request.env['tipo.de.ingresso'].sudo().search([('cod_ingresso', '=', cod_ingresso)], limit=1)
        if not tipo_ingresso:
            response = request.make_response(json.dumps({'error': 'Tipo de Ingresso not found'}), headers=headers)
            response.status_code = 404
            return response

        tipo_ingresso_data = {
            'nome': tipo_ingresso.nome,
            'descricao': tipo_ingresso.descricao,
            'color': tipo_ingresso.color,
            'cod_ingresso': tipo_ingresso.cod_ingresso,
        }
        response = request.make_response(json.dumps({'success': True, 'tipo_ingresso': tipo_ingresso_data}), headers=headers)
        response.status_code = 200
        return response

    @http.route('/api/tipoingresso/create', auth='none', type='json', methods=['POST', 'OPTIONS'], cors='*')
    def create_tipoingresso(self, **kw):

        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        data = request.jsonrequest
        try:
            new_tipo_ingresso = request.env['tipo.de.ingresso'].sudo().create({
                'nome': data.get('nome'),
                'descricao': data.get('descricao'),
                'color': data.get('color'),
                'cod_ingresso': data.get('cod_ingresso'),
            })
            return {'success': True, 'id': new_tipo_ingresso.id}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/tipoingresso/delete/<string:cod_ingresso>', auth='none', type='http', methods=['DELETE', 'OPTIONS'], csrf=False, cors='*')
    def delete_tipoingresso(self, cod_ingresso, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            response = request.make_response(json.dumps({'error': 'invalid token'}), headers=headers)
            response.status_code = 401
            return response
        
        tipo_ingresso = request.env['tipo.de.ingresso'].sudo().search([('cod_ingresso', '=', cod_ingresso)], limit=1)
        if not tipo_ingresso:
            response = request.make_response(json.dumps({'error': 'Tipo de Ingresso not found'}), headers=headers)
            response.status_code = 404
            return response
        
        try:
            tipo_ingresso.unlink()
            response = request.make_response(json.dumps({'success': True}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response

    @http.route(['/api/tipoingresso/update/<string:cod_ingresso>', '/api/tipoingresso/update/<string:cod_ingresso>/<attribute>'], auth='none', type='http', methods=['PUT', 'OPTIONS'], csrf=False, cors='*')
    def update_tipoingresso(self, cod_ingresso, attribute=None, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            response = request.make_response(json.dumps({'error': 'invalid token'}), headers=headers)
            response.status_code = 401
            return response

        tipo_ingresso = request.env['tipo.de.ingresso'].sudo().search([('cod_ingresso', '=', cod_ingresso)], limit=1)
        if not tipo_ingresso:
            response = request.make_response(json.dumps({'error': 'Tipo de Ingresso not found'}), headers=headers)
            response.status_code = 404
            return response

        try:
            data = json.loads(request.httprequest.data)
            update_vals = {}
            if attribute:
                if attribute in ['nome', 'descricao', 'color'] and attribute in data:
                    update_vals[attribute] = data[attribute]
                else:
                    response = request.make_response(json.dumps({'error': 'Invalid attribute or missing data'}), headers=headers)
                    response.status_code = 400
                    return response
            else:
                for attr in ['nome', 'descricao', 'color']:
                    if attr in data:
                        update_vals[attr] = data[attr]

            tipo_ingresso.write(update_vals)
            response = request.make_response(json.dumps({'success': True}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response

class TipoCancelamentoController(http.Controller):

    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True
    
    @http.route('/api/tipocancelamento/all', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_all_tipocancelamento(self, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        try:
            tipo_cancelamento = request.env['tipo.de.cancelamento'].sudo().search_read([], ['nome', 'descricao', 'color', 'cod_cancelamento'])
            response = request.make_response(json.dumps({'success': True, 'tipos de cancelamento': tipo_cancelamento}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response

    @http.route('/api/tipocancelamento/<string:cod_cancelamento>', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_tipocancelamento_by_cod(self, cod_cancelamento, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        tipo_cancelamento = request.env['tipo.de.cancelamento'].sudo().search([('cod_cancelamento', '=', cod_cancelamento)], limit=1)
        if not tipo_cancelamento:
            response = request.make_response(json.dumps({'error': 'Tipo de cancelamento não encontrado'}), headers=headers)
            response.status_code = 404
            return response

        tipo_cancelamento_data = {
            'nome': tipo_cancelamento.nome,
            'descricao': tipo_cancelamento.descricao,
            'color': tipo_cancelamento.color,
            'cod_cancelamento': tipo_cancelamento.cod_cancelamento,
        }
        response = request.make_response(json.dumps({'success': True, 'tipocancelamento': tipo_cancelamento_data}), headers=headers)
        response.status_code = 200
        return response

    @http.route('/api/tipocancelamento/create', auth='none', type='json', methods=['POST', 'OPTIONS'], cors='*')
    def create_tipocancelamento(self, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        data = request.jsonrequest
        try:
            new_tipo_cancelamento = request.env['tipo.de.cancelamento'].sudo().create({
                'nome': data.get('nome'),
                'descricao': data.get('descricao'),
                'color': data.get('color'),
                'cod_cancelamento': data.get('cod_cancelamento'),
            })
            return {'success': True, 'id': new_tipo_cancelamento.id}
        except Exception as e:
            return {'error': str(e)}
        
    @http.route('/api/tipocancelamento/delete/<string:cod_cancelamento>', auth='none', type='http', methods=['DELETE', 'OPTIONS'], csrf=False, cors='*')
    def delete_tipocancelamento(self, cod_cancelamento, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}
        
        tipo_cancelamento = request.env['tipo.de.cancelamento'].sudo().search([('cod_cancelamento', '=', cod_cancelamento)], limit=1)
        if not tipo_cancelamento:
            response = request.make_response(json.dumps({'error': 'Tipo de cancelamento not found'}), headers=headers)
            response.status_code = 404
            return response
        
        try:
            tipo_cancelamento.unlink()
            response = request.make_response(json.dumps({'success': True}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response

    @http.route(['/api/tipocancelamento/update/<string:cod_cancelamento>', '/api/tipocancelamento/update/<string:cod_cancelamento>/<attribute>'], auth='none', type='http', methods=['PUT', 'OPTIONS'], csrf=False, cors='*')
    def update_tipocancelamento(self, cod_cancelamento, attribute=None, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        tipo_cancelamento = request.env['tipo.de.cancelamento'].sudo().search([('cod_cancelamento', '=', cod_cancelamento)], limit=1)
        if not tipo_cancelamento:
            response = request.make_response(json.dumps({'error': 'Tipo de cancelamento not found'}), headers=headers)
            response.status_code = 404
            return response

        try:
            data = json.loads(request.httprequest.data)
            update_vals = {}
            if attribute:
                if attribute in ['nome', 'descricao', 'color'] and attribute in data:
                    update_vals[attribute] = data[attribute]
                else:
                    response = request.make_response(json.dumps({'error': 'Invalid attribute or missing data'}), headers=headers)
                    response.status_code = 400
                    return response
            else:
                for attr in ['nome', 'descricao', 'color']:
                    if attr in data:
                        update_vals[attr] = data[attr]

            tipo_cancelamento.write(update_vals)
            response = request.make_response(json.dumps({'success': True}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response    

class InformaCurriculoController(http.Controller):

    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True

    def find_professor_by_cod(self, cod_professor):
        professor = request.env['res.partner'].sudo().search([
            ('cod_professor', '=', cod_professor),
            ('professor', '=', True),
        ], limit=1)
        if not professor:
            return None
        return professor.id
    
    @http.route('/api/curriculo/all', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_all_curriculo(self, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}
        
        try:
            curriculo = request.env['informa.curriculo'].sudo().search_read([], ['name', 'professor', 'cod_curriculo'])
            response = request.make_response(json.dumps({'success': True, 'curriculo': curriculo}), headers=headers)
            response.status_code = 200
            return response
        
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response

    @http.route('/api/curriculo/<string:cod_curriculo>', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_curriculo_by_cod(self, cod_curriculo, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        curriculo = request.env['informa.curriculo'].sudo().search([('cod_curriculo', '=', cod_curriculo)], limit=1)
        if not curriculo:
            response = request.make_response(json.dumps({'error': 'Currículo não encontrado'}), headers=headers)
            response.status_code = 404
            return response
        
        curriculo_data = {
            'nome': curriculo.name,
            'professor': curriculo.professor.id if curriculo.professor else None,  # Assume que professor é um relacionamento Many2one
            'cod_curriculo': curriculo.cod_curriculo,
        }
        response = request.make_response(json.dumps({'success': True, 'curriculo': curriculo_data}), headers=headers)
        response.status_code = 200
        return response

    @http.route('/api/curriculo/create', auth='none', type='json', methods=['POST', 'OPTIONS'], cors='*')
    def create_curriculo(self, **kw):
        # Verifica o token de autenticação do cliente
        token = request.httprequest.headers.get('Token')
        if not self.verify_client_token(token):
            return {'error': 'invalid token'}

        data = request.jsonrequest
        professor = self.find_professor_by_cod(data.get('cod_professor'))
        if not professor:
            return {'error': 'Professor not found'}

        try:
            new_curriculo = request.env['informa.curriculo'].sudo().create({
                'name': data.get('name'),
                'professor': professor,  # Ajuste conforme o nome correto do campo
                'cod_curriculo': data.get('cod_curriculo'),
            })
            return {'success': True, 'id': new_curriculo.id}
        except Exception as e:
            return {'error': str(e)}
        
    @http.route('/api/curriculo/delete/<string:cod_curriculo>', auth='none', type='http', methods=['DELETE', 'OPTIONS'], csrf=False, cors='*')
    def delete_curriculo(self, cod_curriculo, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            response = request.make_response(json.dumps({'error': 'invalid token'}), headers=headers)
            response.status_code = 401
            return response
        
        curriculo = request.env['informa.curriculo'].sudo().search([('cod_curriculo', '=', cod_curriculo)], limit=1)
        if not curriculo:
            response = request.make_response(json.dumps({'error': 'Currículo not found'}), headers=headers)
            response.status_code = 404
            return response
        
        try:
            curriculo.unlink()
            response = request.make_response(json.dumps({'success': True}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response


    @http.route(['/api/curriculo/update/<string:cod_curriculo>', '/api/curriculo/update/<string:cod_curriculo>/<attribute>'], auth='none', type='http', methods=['PUT', 'OPTIONS'], csrf=False, cors='*')
    def update_curriculo(self, cod_curriculo, attribute=None, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        curriculo = request.env['informa.curriculo'].sudo().search([('cod_curriculo', '=', cod_curriculo)], limit=1)
        if not curriculo:
            return request.make_response(json.dumps({'error': 'Curriculo not found'}), headers=headers)

        try:
            # Ajuste para ler o corpo da requisição HTTP corretamente
            data = json.loads(request.httprequest.data.decode('utf-8'))  # Decodifica e converte o JSON para dicionário
            update_vals = {}
        
            if attribute:
                # Atualiza apenas o atributo especificado, se estiver presente nos dados
                if attribute in ['name', 'professor'] and attribute in data:
                    if attribute == 'professor':
                        professor_id = self.find_professor_by_cod(data[attribute])
                        if not professor_id:
                            response = request.make_response(json.dumps({'error': 'Professor not found'}), headers=headers)
                            return response
                        update_vals['professor'] = professor_id
                    else:
                        update_vals[attribute] = data[attribute]
                else:
                    response = request.make_response(json.dumps({'error': 'Invalid attribute or missing data'}), headers=headers)
                    return response
            else:
                # Atualiza todos os campos permitidos se nenhum atributo específico for fornecido
                if 'name' in data:
                    update_vals['name'] = data['name']
                if 'cod_professor' in data:
                    professor_id = self.find_professor_by_cod(data['cod_professor'])
                    if not professor_id:
                        response = request.make_response(json.dumps({'error': 'Professor not found'}), headers=headers)
                        return response
                    update_vals['professor'] = professor_id

                curriculo.write(update_vals)
                return request.make_response(json.dumps({'success': True}), headers=headers)
        except Exception as e:
            return request.make_response(json.dumps({'error': str(e)}), headers=headers)
        

class InformaCurriculoVariantController(http.Controller):

    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True
    
        
    @http.route('/api/curriculovariant/all', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_all_curriculovariant(self, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        try:
            curriculo_variants = request.env['informa.curriculo.variant'].sudo().search_read([], ['name', 'create_date', 'variation_number', 'disciplina_ids', 'sequence', 'cod_variante', 'days_to_release', 'curriculo_id'])
            for variant in curriculo_variants:
                if 'create_date' in variant:
                    variant['create_date'] = variant['create_date'].strftime("%Y-%m-%dT%H:%M:%S")
            response = request.make_response(json.dumps({'success': True, 'curriculovariant': curriculo_variants}), headers=headers)
            response.status_code = 200
            return response
        
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response
        
    @http.route('/api/curriculovariant/<string:cod_variante>', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_curriculo_var_by_cod(self, cod_variante, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        # Verifica o token de autenticação do cliente
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        try:
            curriculo_var = request.env['informa.curriculo.variant'].sudo().search([('cod_variante', '=', cod_variante)], limit=1)
            if not curriculo_var:
                response = request.make_response(json.dumps({'error': 'Variante de currículo não encontrado'}), headers=headers)
                return response
            
            # Preparação dos dados, incluindo o tratamento da lista de disciplinas
            disciplinas = curriculo_var.disciplina_ids.mapped(lambda d: {'id': d.id, 'nome': d.name})
            
            curriculo_var_data = {
                'nome': curriculo_var.name,
                'data_de_criacao': curriculo_var.create_date.isoformat() if curriculo_var.create_date else None,
                'numero_de_variacao': curriculo_var.variation_number,
                'disciplinas': disciplinas,
                'sequencia': curriculo_var.sequence,
                'dias_para_liberar_conteudo': curriculo_var.days_to_release,
                'curriculo_id': curriculo_var.curriculo_id.id if curriculo_var.curriculo_id else None,
                'cod_variante': curriculo_var.cod_variante,
            }
            
            response = request.make_response(json.dumps({'success': True, 'curriculovariante': curriculo_var_data}), headers=headers)
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            return response

    @http.route('/api/curriculovariant/create', auth='none', type='json', methods=['POST', 'OPTIONS'], cors='*')
    def create_curriculovariant(self, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        # Verifica o token de autenticação do cliente
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        data = request.jsonrequest
        # Convertir lista de códigos de disciplinas em IDs
        disciplina_ids = request.env['informa.disciplina'].search([('cod_disciplina', 'in', data.get('disciplina_codigos', []))]).ids
        if not disciplina_ids:
            return {'error': 'No valid disciplinas found'}
        
        disciplina_ids_relation = [(6, 0, disciplina_ids)]
        curriculo_id = request.env['informa.curriculo'].search([('cod_curriculo', '=', data.get('cod_curriculo'))], limit=1)
        if not curriculo_id:
            return {'error': 'Curriculo not found'}

        try:
            new_variant = request.env['informa.curriculo.variant'].sudo().create({
                'name': data.get('name'),
                'disciplina_ids': disciplina_ids_relation,
                'sequence': data.get('sequence'),
                'days_to_release': data.get('days_to_release', 7),
                'default_days_to_release': data.get('default_days_to_release', 7),
                'curriculo_id': curriculo_id.id,
                'cod_variante': data.get('cod_variante'),
            })
            return {'success': True, 'id': new_variant.id}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/curriculovariant/delete/<string:cod_variante>', auth='none', type='http', methods=['DELETE', 'OPTIONS'], csrf=False, cors='*')
    def delete_curriculovariant(self, cod_variante, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        # Verifica o token de autenticação do cliente
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}
        
        variant = request.env['informa.curriculo.variant'].sudo().search([('cod_variante', '=', cod_variante)], limit=1)
        if not variant:
            response = {'error': 'Curriculo Variant not found'}
            return response

        try:
            variant.unlink()
            response = {'success': True}
            return response
        except Exception as e:
            response = {'error': str(e)}
            return response

    @http.route(['/api/curriculovariant/update/<string:cod_variante>'], auth='none', type='http', methods=['PUT', 'OPTIONS'], cors='*', csrf=False)
    def update_curriculovariant(self, cod_variante, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        # Verifica o token de autenticação do cliente
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        try:
            # Ajuste para ler o corpo da requisição HTTP como JSON
            data = json.loads(request.httprequest.data.decode('utf-8'))
            variant = request.env['informa.curriculo.variant'].sudo().search([('cod_variante', '=', cod_variante)], limit=1)

            if not variant:
                response = {'error': 'Curriculo Variant not found'}
                return response

            # Processamento de atributos específicos ou atualização de todos os campos permitidos
            update_vals = {key: value for key, value in data.items() if key in variant._fields}
            variant.write(update_vals)

            response = {'success': True}
            return response
        except Exception as e:
            response = {'error': str(e)}
            return response
        
class InformaCursosController(http.Controller):

    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True

    def get_curriculo_id_by_cod(self, cod_curriculo):
        curriculo = request.env['informa.curriculo'].sudo().search([('cod_curriculo', '=', cod_curriculo)], limit=1)
        if not curriculo:
            return None
        return curriculo.id

    def get_variant_curriculo_id_by_cod(self, cod_variante, curriculo_id):
        variant = request.env['informa.curriculo.variant'].sudo().search([
            ('cod_variante', '=', cod_variante),
            ('curriculo_id', '=', curriculo_id),
        ], limit=1)
        if not variant:
            return None
        return variant.id
        
    @http.route('/api/cursos/all', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_all_curso(self, **kw):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        # Verifica o token de autenticação do cliente
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        try:
            cursos = request.env['informa.cursos'].sudo().search_read([], [
                'name', 'status_do_certificado', 'numero_matricula', 'cod_curso',
                'curriculo_id', 'variant_curriculo_id', 'disciplina_ids', 'formato_nota', 'tempo_de_conclusao'
            ])
            
            response = request.make_response(json.dumps({'success': True, 'cursos': cursos}), headers=headers)
            response.status_code = 200
            return response
        except Exception as e:
            response = request.make_response(json.dumps({'error': str(e)}), headers=headers)
            response.status_code = 500
            return response

    @http.route('/api/cursos/<string:cod_curso>', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_curso_by_cod(self, cod_curso, **kw):
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            error_response = json.dumps({'error': 'invalid token'})
            return request.make_response(error_response, headers=headers, status=401)

        try:
            curso = request.env['informa.cursos'].sudo().search([('cod_curso', '=', cod_curso)], limit=1)
            if not curso:
                error_response = json.dumps({'error': 'Curso não encontrado'})
                return request.make_response(error_response, headers=headers, status=404)
            
            # Aqui você precisa garantir que todos os campos relacionados sejam serializáveis
            curso_data = {
                'name': curso.name,
                'cod_curso': curso.cod_curso,
                'curriculo_id': curso.curriculo_id.id if curso.curriculo_id else None,
                'variant_curriculo_id': curso.variant_curriculo_id.id if curso.variant_curriculo_id else None,
                'formato_nota': curso.formato_nota,
                'tempo_de_conclusao': curso.tempo_de_conclusao,
            }
            success_response = json.dumps({'success': True, 'curso': curso_data})
            return request.make_response(success_response, headers=headers)
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            return request.make_response(error_response, headers=headers, status=500)

    @http.route('/api/cursos/create', auth='none', type='json', methods=['POST', 'OPTIONS'], cors='*')
    def create_curso(self, **kw):

        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        data = request.jsonrequest
        curriculo_id = self.get_curriculo_id_by_cod(data.get('cod_curriculo'))
        if not curriculo_id:
            return {'error': 'Curriculo not found'}

        variant_curriculo_id = self.get_variant_curriculo_id_by_cod(data.get('cod_variante'), curriculo_id) if 'cod_variante' in data else None
        if 'cod_variante' in data and not variant_curriculo_id:
            return {'error': 'Variant Curriculo not found or not matching the Curriculo'}

        try:
            new_curso = request.env['informa.cursos'].sudo().create({
                'name': data.get('name'),
                'cod_curso': data.get('cod_curso'),
                'curriculo_id': curriculo_id,
                'variant_curriculo_id': variant_curriculo_id,
                'disciplina_ids': [(6, 0, data.get('disciplina_ids'))] if 'disciplina_ids' in data else [],
                'tempo_de_conclusao': data.get('tempo_de_conclusao'),
                'formato_nota': data.get('formato_nota'),
            })
            return {'success': True, 'id': new_curso.id}
        except Exception as e:
            return {'error': str(e)}        

    @http.route('/api/cursos/update/<string:cod_curso>', auth='none', type='http', methods=['PUT', 'OPTIONS'], cors='*', csrf=False)
    def update_curso(self, cod_curso, **kw):
        headers = {'Content-Type': 'application/json'}

        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            error_response = json.dumps({'error': 'invalid token'})
            return request.make_response(error_response, headers=headers)

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            curso = request.env['informa.cursos'].sudo().search([('cod_curso', '=', cod_curso)], limit=1)

            if not curso:
                error_response = json.dumps({'error': 'Curso Não encontrado'})
                return request.make_response(error_response, headers=headers)

            update_vals = {key: value for key, value in data.items() if key in curso._fields}
            curso.write(update_vals)

            success_response = json.dumps({'success': True})
            return request.make_response(success_response, headers=headers)
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            return request.make_response(error_response, headers=headers)  
        

    @http.route('/api/cursos/delete/<string:cod_curso>', auth='none', type='http', methods=['DELETE', 'OPTIONS'], csrf=False, cors='*')
    def delete_curso(self, cod_curso, **kw):
        headers = {'Content-Type': 'application/json'}

        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            error_response = json.dumps({'error': 'invalid token'})
            return request.make_response(error_response, headers=headers)

        curso = request.env['informa.cursos'].sudo().search([('cod_curso', '=', cod_curso)], limit=1)

        if not curso:
            error_response = json.dumps({'error': 'curso não encontrado'})
            return request.make_response(error_response, headers=headers)

        try:
            curso.unlink()
            success_response = json.dumps({'success': True})
            return request.make_response(success_response, headers=headers)
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            return request.make_response(error_response, headers=headers)
        
class InformaMatriculaController(http.Controller):

    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True

    def get_tipo_ingresso_id_by_cod(self, cod_ingresso):
        tipo_ingresso = request.env['tipo.de.ingresso'].sudo().search([('cod_ingresso', '=', cod_ingresso)], limit=1)
        return tipo_ingresso.id if tipo_ingresso else None

    def get_curriculo_id_by_cod(self, cod_curriculo):
        curriculo = request.env['informa.curriculo'].sudo().search([('cod_curriculo', '=', cod_curriculo)], limit=1)
        return curriculo.id if curriculo else None

    def get_variant_curriculo_id_by_cod(self, cod_variante, curriculo_id):
        variant = request.env['informa.curriculo.variant'].sudo().search([
            ('cod_variante', '=', cod_variante),
            ('curriculo_id', '=', curriculo_id),
        ], limit=1)
        return variant.id if variant else None
    
    @http.route('/api/matricula/all', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_all_matricula(self, **kw):
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization', 
        }

        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            error_response = json.dumps({'error': 'invalid token'})
            return request.make_response(error_response, headers=headers, status=401)
        
        try:
            matriculas = request.env['informa.matricula'].sudo().search_read([], [
                'status_do_certificado', 'variant_curriculo_id', 'disciplina_ids', 'grupo_disciplina_id',
                'cod_curso', 'matricula_aluno', 'numero_matricula', 'tipo_de_cancelamento', 'tipo_de_ingresso',
                'data_prorrogacao', 'prorrogacao', 'data_original_certificacao', 'data_provavel_certificacao',
                'regiao', 'justificativa_cancelamento', 'inscricao_ava', 'email', 'telefone', 'nome_do_aluno',
                'curso', 'prazo_exp_certf_dias', 'numero_de_modulo'
            ])

            processed_matriculas = []
            for matricula in matriculas:
                # Processa cada campo de data para o formato ISO, se presente
                for field in ['data_prorrogacao', 'data_original_certificacao', 'data_provavel_certificacao', 'inscricao_ava']:
                    if matricula[field]:
                        matricula[field] = matricula[field].isoformat()
                processed_matriculas.append(matricula)

            success_response = json.dumps({'success': True, 'matricula': processed_matriculas})
            return request.make_response(success_response, headers=headers)
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            return request.make_response(error_response, headers=headers, status=500)

    @http.route('/api/matricula/<string:numero_matricula>', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_matricula_by_cod(self, numero_matricula, **kw):
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            error_response = json.dumps({'error': 'invalid token'})
            return request.make_response(error_response, headers=headers, status=401)

        matricula = request.env['informa.matricula'].sudo().search([('numero_matricula', '=', numero_matricula)], limit=1)
        if not matricula:
            error_response = json.dumps({'error': 'Matricula não encontrada'})
            return request.make_response(error_response, headers=headers, status=404)
        
        matricula_data = {
            'status_do_certificado': matricula.status_do_certificado,
            'variant_curriculo_id': matricula.variant_curriculo_id.id if matricula.variant_curriculo_id else None,
            'disciplina_ids': [d.id for d in matricula.disciplina_ids],
            'grupo_disciplina_id': matricula.grupo_disciplina_id.id if matricula.grupo_disciplina_id else None,
            'cod_curso': matricula.cod_curso,
            'matricula_aluno': matricula.matricula_aluno,
            'numero_matricula': matricula.numero_matricula,
            'tipo_de_cancelamento': matricula.tipo_de_cancelamento.id if matricula.tipo_de_cancelamento else None,
            'tipo_de_ingresso': matricula.tipo_de_ingresso.id if matricula.tipo_de_ingresso else None,
            'data_prorrogacao': matricula.data_prorrogacao.isoformat() if matricula.data_prorrogacao else None,
            'data_original_certificacao': matricula.data_original_certificacao.isoformat() if matricula.data_original_certificacao else None,
            'data_provavel_certificacao': matricula.data_provavel_certificacao.isoformat() if matricula.data_provavel_certificacao else None,
            'regiao': matricula.regiao,
            'justificativa_cancelamento': matricula.justificativa_cancelamento,
            'inscricao_ava': matricula.inscricao_ava.isoformat() if matricula.inscricao_ava else None,
            'email': matricula.email,
            'telefone': matricula.telefone,
            'nome_do_aluno': matricula.nome_do_aluno.name if matricula.nome_do_aluno else None,
            'curso': matricula.curso.id if matricula.curso else None,
            'prazo_exp_certf_dias': matricula.prazo_exp_certf_dias,
            'numero_de_modulo': matricula.numero_de_modulo,
        }
        
        success_response = json.dumps({'success': True, 'Matricula': matricula_data})
        return request.make_response(success_response, headers=headers) 

    # Endpoint para criar matrícula
    @http.route('/api/matricula/create', auth='none', type='json', methods=['POST', 'OPTIONS'], cors='*')
    def create_matricula(self, **kw):
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # lidando com o "OPTIONS" na requisição
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        #lidando com o token
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        data = request.jsonrequest

        # Resolvendo IDs necessários
        tipo_ingresso_id = self.get_tipo_ingresso_id_by_cod(data.get('cod_ingresso'))
        if not tipo_ingresso_id:
            return {'error': 'Tipo de Ingresso not found'}
        
        grupo_disciplina_id = self.get_curriculo_id_by_cod(data.get('cod_curriculo'))
        if not grupo_disciplina_id:
            return {'error': 'Curriculo not found'}

        variant_curriculo_id = self.get_variant_curriculo_id_by_cod(data.get('cod_variante'), grupo_disciplina_id) if 'cod_variante' in data else None
        if 'cod_variante' in data and not variant_curriculo_id:
            return {'error': 'Variant Curriculo not found or not matching the Curriculo'}

        try:
            new_matricula = request.env['informa.matricula'].sudo().create({
                'tipo_de_ingresso': tipo_ingresso_id,
                'grupo_disciplina_id': grupo_disciplina_id,
                'variant_curriculo_id': variant_curriculo_id,
                'allow_grade_editing': True,
                'nome_do_aluno': data.get('nome_do_aluno'),
                'curso': data.get('curso'),
                'regiao': 'AVA',
                'inscricao_ava': data.get('inscricao_ava'),
                'email': data.get('email'),
                'telefone': data.get('telefone'),
                'numero_matricula': data.get('numero_matricula'),
                'status_do_certificado': 'CURSANDO',
            })
            return {'success': True, 'id': new_matricula.id}
        except Exception as e:
            return {'error': str(e)}        

    @http.route('/api/matricula/update/<string:numero_matricula>', auth='none', type='http', methods=['PUT', 'OPTIONS'], cors='*', csrf=False)
    def update_matricula(self, numero_matricula, **kw):
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            error_response = json.dumps({'error': 'invalid token'})
            response = request.make_response(error_response, headers=headers)
            response.status_code = 401
            return response
        
        try:
            # Garante que estamos lidando com um dicionário após decodificar o JSON
            data = json.loads(request.httprequest.data.decode('utf-8')) if request.httprequest.data else {}
            matricula = request.env['informa.matricula'].sudo().search([('numero_matricula', '=', numero_matricula)], limit=1)
            
            if not matricula:
                error_response = json.dumps({'error': 'Matrícula não encontrada'})
                response = request.make_response(error_response, headers=headers)
                response.status_code = 404
                return response
                
            # Agora, usamos data.get() com segurança, sabendo que data é um dicionário
            update_vals = {key: value for key, value in data.items() if key in matricula._fields}
            matricula.write(update_vals)
            
            success_response = json.dumps({'success': True})
            return request.make_response(success_response, headers=headers)
            
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            response = request.make_response(error_response, headers=headers)
            response.status_code = 500
            return response

    @http.route('/api/matricula/<string:numero_matricula>', auth='none', type='http', methods=['DELETE', 'OPTIONS'], csrf=False, cors='*')
    def delete_matricula(self, numero_matricula, **kw):

        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        #lidando com o OPTIONS
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        #lidando com o Token
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            error_response = json.dumps({'error': 'invalid token'})
            return request.make_response(error_response, headers=headers)

        matricula = request.env['informa.matricula'].sudo().search([('numero_matricula', '=', numero_matricula)], limit=1)
        
        if not matricula:
            error_response = json.dumps({'error': 'Matrícula não encontrada'})
            return request.make_response(error_response, headers=headers)

        try:
            matricula.unlink()
            success_response = json.dumps({'success': True})
            return request.make_response(success_response, headers=headers)
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            return request.make_response(error_response, headers=headers)
 
class InformaRegistroAluno(http.Controller): 
    
    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True
        
    # Mostrar todas as informações de registro de uma matricula    
    @http.route('/api/registrodisciplina/<string:numero_matricula>', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_registro_disciplina_by_matricula(self, numero_matricula, **kw):
        
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            error_response = json.dumps({'error': 'invalid token'})
            return request.make_response(error_response, headers=headers, status=401)

        try:
            matricula = request.env['informa.matricula'].sudo().search([('numero_matricula', '=', numero_matricula)], limit=1)
            if not matricula:
                return {'error': 'Matrícula not found'}

            registros = request.env['informa.registro_disciplina'].sudo().search_read([('matricula_id', '=', matricula.id)], ['curso_id', 'disciplina_id', 'nota', 'status'])
            for registro in registros:
                registro['curso_nome'] = registro['curso_id'][1]  # Assume curso_id comes as [id, name]
                registro['disciplina_nome'] = registro['disciplina_id'][1]  # Assume disciplina_id comes as [id, name]
                del registro['curso_id'], registro['disciplina_id']  # Cleanup
            
            success_response = json.dumps({'success': True, 'matricula': registros})
            return request.make_response(success_response, headers=headers)
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            return request.make_response(error_response, headers=headers, status=500)
        
    @http.route('/api/matricula/update/<string:numero_matricula>', auth='none', type='http', methods=['PUT', 'OPTIONS'], cors='*', csrf=False)
    def update_matricula(self, numero_matricula, **kw):
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            error_response = json.dumps({'error': 'invalid token'})
            response = request.make_response(error_response, headers=headers)
            response.status_code = 401
            return response
        
        try:
            # Garante que estamos lidando com um dicionário após decodificar o JSON
            data = json.loads(request.httprequest.data.decode('utf-8')) if request.httprequest.data else {}
            matricula = request.env['informa.matricula'].sudo().search([('numero_matricula', '=', numero_matricula)], limit=1)
            
            if not matricula:
                error_response = json.dumps({'error': 'Matrícula não encontrada'})
                response = request.make_response(error_response, headers=headers)
                response.status_code = 404
                return response
                
            # Agora, usamos data.get() com segurança, sabendo que data é um dicionário
            update_vals = {key: value for key, value in data.items() if key in matricula._fields}
            matricula.write(update_vals)
            
            success_response = json.dumps({'success': True})
            return request.make_response(success_response, headers=headers)
            
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            response = request.make_response(error_response, headers=headers)
            response.status_code = 500
            return response
    
    # Endpoint para Editar a Nota de um Registro de Disciplina
    @http.route('/api/registrodisciplina/editnota/<string:numero_matricula>/<string:cod_disciplina>/<string:nova_nota>', auth='none', type='json', methods=['PUT', 'OPTIONS'], cors='*', csrf=False)
    def edit_nota_registro_disciplina(self, numero_matricula, cod_disciplina, nova_nota, **kw):
        
        if request.httprequest.method == 'OPTIONS':
            headers = {'Content-Type': 'application/json'}
            return request.make_response(json.dumps({}), headers=headers)
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'},  # Retorno direto do dicionário com o status HTTP
        
        try:
            matricula = request.env['informa.matricula'].sudo().search([('numero_matricula', '=', numero_matricula)], limit=1)
            if not matricula or not matricula.allow_grade_editing:
                return {'error': 'Matrícula not found or grade editing not allowed'},

            disciplina = request.env['informa.disciplina'].sudo().search([('cod_disciplina', '=', cod_disciplina)], limit=1)
            if not disciplina:
                return {'error': 'Disciplina not found'},

            registro = request.env['informa.registro_disciplina'].sudo().search([('matricula_id', '=', matricula.id), ('disciplina_id', '=', disciplina.id)], limit=1)
            if not registro:
                return {'error': 'Registro not found'},

            registro.write({'nota': nova_nota})
            return {'success': True}, # Sucesso, retorno direto do dicionário com o status HTTP
        except Exception as e:
            return {'error': str(e)}  # Retorno direto do dicionário com o status HTTP para erros de servidor
        
class RespartnerAPI(http.Controller): 

    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True

    #faz a criação do aluno, considerando  'l10n_br_cnpj_cpf', 'aluno', 'professor', 'name', 'email' como obrigatório
    #o contato criado deve ter aluno ou professor com a informação como True
    @http.route('/api/res_partner/create', auth='none', type='json', methods=['POST', 'OPTIONS'], cors='*')
    def create_res_partner(self, **post):
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)  

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        data = request.jsonrequest
        required_fields = ['l10n_br_cnpj_cpf_formatted', 'name', 'email']
        for field in required_fields:
            if field not in data or not data[field]:
                return {'error': f'{field} is required'}

        if not data.get('aluno') and not data.get('professor'):
            return {'error': 'At least one of aluno or professor must be True'}

        if data.get('aluno'):
            data['matricula_aluno'] = self._generate_unique_matricula_aluno()

        if data.get('professor'):
            data['cod_professor'] = self._generate_unique_matricula_professor()

        try:
            new_partner = request.env['res.partner'].sudo().create(data)
            return {'success': True, 'partner_id': new_partner.id}
        except Exception as e:
            return {'error': str(e)}

    def _generate_unique_matricula_aluno(self):
        Partner = request.env['res.partner']
        while True:
            matricula = self._generate_matricula_aluno()
            existing_partner = Partner.sudo().search([('matricula_aluno', '=', matricula)], limit=1)
            if not existing_partner:
                return matricula

    def _generate_matricula_aluno(self):
        current_year = date.today().year
        semester = '01' if date.today().month <= 6 else '02'
        last_digits = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        return f"{current_year}{semester}{last_digits}"

    def _generate_unique_matricula_professor(self):
        Partner = request.env['res.partner']
        while True:
            cod = self._generate_matricula_professor()
            existing_partner = Partner.sudo().search([('cod_professor', '=', cod)], limit=1)
            if not existing_partner:
                return cod

    def _generate_matricula_professor(self):
        current_year = date.today().year
        faculdade = "FG"
        last_digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        return f"{faculdade}{current_year}{last_digits}"
        
    #edição de contatos pelo codigo de matricula e do professor
    @http.route(['/api/res_partner/edit_by_registro/<string:matricula>',
                '/api/res_partner/edit_by_cod_professor/<string:cod_professor>'], auth='none', type='json', methods=['PUT', 'OPTIONS'], cors='*')
    def edit_res_partner_by_identification(self, matricula=None, cod_professor=None, **post):
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'PUT, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)                
        
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return {'error': 'invalid token'}

        data = request.jsonrequest
        domain = []
        if matricula:
            domain = [('matricula_aluno', '=', matricula), ('aluno', '=', True)]
        elif cod_professor:
            domain = [('cod_professor', '=', cod_professor), ('professor', '=', True)]

        partner = request.env['res.partner'].sudo().search(domain, limit=1)
        if not partner:
            return {'error': 'Partner not found'}

        try:
            partner.sudo().write(data)
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}

    #Delete de contatos pelo codigo de matricula e do professor
    @http.route(['/api/res_partner/delete_by_matricula/<string:matricula>',
                 '/api/res_partner/delete_by_cod_professor/<string:cod_professor>'],
                auth='none', type='http', methods=['DELETE', 'OPTIONS'], csrf=False, cors='*')    
    def delete_partner(self, matricula=None, cod_professor=None, **kwargs):        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }        
        # Handle preflight "OPTIONS" request
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=headers)                
        # Verifica se o token de cliente é válido
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return Response(json.dumps({'error': 'invalid token'}), status=401, mimetype='application/json')
        # Define o domínio de busca baseado nos parâmetros fornecidos
        domain = [('matricula_aluno', '=', matricula)] if matricula else [('cod_professor', '=', cod_professor)]
        partner = request.env['res.partner'].sudo().search(domain, limit=1)
        # Verifica se o parceiro foi encontrado
        if not partner:
            return Response(json.dumps({'error': 'Partner not found'}), status=404, mimetype='application/json')
        # Tenta excluir o parceiro e retorna a resposta apropriada
        try:
            partner.sudo().unlink()
            return Response(json.dumps({'success': 'Partner deleted successfully'}), status=200, mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')
        
class PartnerAPI(http.Controller):
    
    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True    
    
    @http.route('/api/professors/all', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_all_professors(self, **kw):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=self.get_headers())

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return self.error_response('invalid token', 401)

        try:
            professors = request.env['res.partner'].sudo().search_read(
                [('professor', '=', True)],
                ['name', 'email', 'phone', 'cod_professor']
            )
            return self.success_response({'professors': professors})
        except Exception as e:
            return self.error_response(str(e), 500)
        
    @http.route('/api/students/all', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_all_students(self, **kw):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=self.get_headers())

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return self.error_response('invalid token', 401)

        try:
            students = request.env['res.partner'].sudo().search_read(
                [('aluno', '=', True)],
                ['name', 'email', 'phone', 'matricula_aluno']
            )
            return self.success_response({'students': students})
        except Exception as e:
            return self.error_response(str(e), 500)
    
    @http.route('/api/professor/<string:rp>', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_professor_by_rp(self, rp, **kw):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=self.get_headers())

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return self.error_response('invalid token', 401)

        try:
            professor = request.env['res.partner'].sudo().search_read(
                [('cod_professor', '=', rp), ('professor', '=', True)],
                ['name', 'email', 'phone', 'cod_professor']
            )
            if not professor:
                return self.error_response('Professor not found', 404)
            return self.success_response({'professor': professor[0]})
        except Exception as e:
            return self.error_response(str(e), 500)

    @http.route('/api/student/<string:ra>', auth='none', type='http', methods=['GET', 'OPTIONS'], cors='*')
    def get_student_by_ra(self, ra, **kw):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response('', headers=self.get_headers())

        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return self.error_response('invalid token', 401)

        try:
            student = request.env['res.partner'].sudo().search_read(
                [('matricula_aluno', '=', ra), ('aluno', '=', True)],
                ['name', 'email', 'phone', 'matricula_aluno', 'curso_id']
            )
            if not student:
                return self.error_response('Student not found', 404)
            for s in student:
                s['curso_id'] = s['curso_id'][1] if s['curso_id'] else None
            return self.success_response({'student': student[0]})
        except Exception as e:
            return self.error_response(str(e), 500)

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }

    def success_response(self, data):
        return request.make_response(json.dumps({'success': True, **data}), headers=self.get_headers())

    def error_response(self, error, status):
        response = request.make_response(json.dumps({'error': error}), headers=self.get_headers())
        response.status = status
        return response

class AuditLogReportAPI(http.Controller):
    
    def verify_client_token(self, token):
        client = request.env['informa.cliente'].sudo().search([('token', '=', token)], limit=1)
        if not client:
            return False
        return True
    
    @http.route('/api/audit_logs', auth='none', type='http', methods=['GET'], cors='*')
    def get_audit_logs(self, date_from=None, date_to=None, model_code=None, **kw):
        # Preparar cabeçalhos da resposta
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # Verificar token de autenticação
        if not self.verify_client_token(request.httprequest.headers.get('Token')):
            return request.make_response(json.dumps({'error': 'Invalid token'}), headers=headers, status=401)
        
        domain = []  # Domínio base vazio para buscar todos os registros se nenhum filtro for fornecido
        
        # Filtrar registros por intervalo de datas
        if date_from:
            date_from_dt = datetime.strptime(date_from, "%d-%m-%Y")
            if date_to:
                date_to_dt = datetime.strptime(date_to, "%d-%m-%Y") + timedelta(days=1)  # Incluir o dia inteiro
                domain.append(('change_date', '>=', date_from_dt.strftime("%d-%m-%Y 00:00:00")))
                domain.append(('change_date', '<', date_to_dt.strftime("%d-%m-%Y 00:00:00")))
            else:
                # Apenas um dia específico
                domain.append(('change_date', '>=', date_from_dt.strftime("%d-%m-%Y 00:00:00")))
                domain.append(('change_date', '<', (date_from_dt + timedelta(days=1)).strftime("%d-%m-%Y 00:00:00")))

        # Filtrar registros por código de modelo
        if model_code:
            domain.append(('model_code', '=', model_code))

        # Realizar a busca no banco de dados
        logs = request.env['audit.log.report'].sudo().search_read(domain, [
            'model_name', 'action', 'field_name', 'old_value', 'new_value', 'user_id', 'change_date', 'model_code'
        ])

        # Preparar dados para a resposta
        result = []
        for log in logs:
            result.append({
                'model_name': log['model_name'],
                'action': log['action'],
                'field_name': log['field_name'],
                'old_value': log['old_value'],
                'new_value': log['new_value'],
                'user_id': log['user_id'][1] if log['user_id'] else '',
                'change_date': log['change_date'].strftime("%d-%m-%Y %H:%M:%S") if log['change_date'] else '',
                'model_code': log['model_code']
            })
        
        return request.make_response(json.dumps({'success': True, 'audit_logs': result}), headers=headers)