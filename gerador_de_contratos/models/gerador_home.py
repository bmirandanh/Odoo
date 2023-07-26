from odoo import api, fields, models
from odoo.addons.base.models.qweb import QWeb
from odoo import http
import json
import pdfkit
import werkzeug
from odoo.http import request, Controller, route
import json
import locale
from odoo.addons.web.controllers.main import ensure_db
import base64
import bs4
from bs4 import BeautifulSoup
from werkzeug.wrappers import Response
import pdfkit
import logging
import re
from odoo.exceptions import ValidationError
import copy
import openai
import requests


_logger = logging.getLogger(__name__)


from bs4 import BeautifulSoup

class GenerateSimplifiedContract(models.Model):
    _name = 'generate.simplified.contract'

    prompt = fields.Text(string='Prompt')
    response = fields.Html(string='Response')

    MAX_ARTICLES_PER_BATCH = 10
    MAX_TOKENS_PER_ARTICLE = 320


    def clean_html_content(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()

        # list of unwanted strings
        unwanted_strings = [
            "</p>", "\\xa", "<td colspan=\"4\">", "xa0", "\xa0", "<p>", "<strong>", "</strong>", "</p>", "</td>", 
            "\\", "</tr>", "</blockquote>", "_________________________________________________", "<br />", "|", "<br", 
            '<p style="text-align: center">'
        ]


        # replace unwanted strings with ''
        for s in unwanted_strings:
            text = text.replace(s, '')

        # use regular expression to replace multiple spaces with a single space
        text = re.sub(' +', ' ', text)

        return text

    def make_gpt3_request(self, prompt):
        openai.api_key = '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'

        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature=0.38,
                max_tokens=256,
                top_p=1,
                frequency_penalty=2,
                presence_penalty=2
            )
            return response['choices'][0]['text']
        except Exception as e:
            return str(e)

    def create_prompts(self):
        articles = self.env['create.article'].search([])

        batches = [articles[i:i+self.MAX_ARTICLES_PER_BATCH] for i in range(0, len(articles), self.MAX_ARTICLES_PER_BATCH)]
        prompts = []

        for batch in batches:
            batch_prompts = ["Para cada artigos de contratos, temos códigos únicos. Vou te apresentar nossos artigos e seus códigos únicos, analise, pois farei uma pergunta sobre eles logo após: "]
            for article in batch:
                content = self.clean_html_content(article.content)  # Clean the HTML content here
                if len(content.split()) <= self.MAX_TOKENS_PER_ARTICLE:
                    prompt = {"prompt": content, "completion": article.id}  # Use the cleaned content here
                    batch_prompts.append(str(prompt))
            batch_prompts.append("Considerando a conversa até aqui, Traga o (ou os) código(s) único(s) dos campos de completion, um ou mais artigo(s), mas apenas os que aborde(m): "+self.prompt+", Formate a resposta entre tags [ANSTART]RESPOSTA[ANEND] conforme o exemplo [ANSTART]CODIGO1,CODIGO2,CODIGO3,...[ANEND], lembrando, apenas os artigos que tenha "+self.prompt+", se não houver nenhum, escreva 'N/D', não coloque nenhum completion, que não possua o tema, é a regra que deve sempre seguir, apenas artigos do solicitado, que foi o tema "+self.prompt+", com este tema, pegue os artigos para a criação de um contrato completo com o que foi analisado: ")
            prompts.append(' '.join(batch_prompts))
        return prompts

    def button_generate_contract(self):
        prompts = self.create_prompts()

        responses = []
        for prompt in prompts:
            print(f"Sending prompt to GPT-3: {prompt}")  # print statement added here to visualize the prompt before sending to GPT-3
            response = self.make_gpt3_request(prompt)
            print(f"GPT-3 Response: {response}")  # Print GPT-3 response
            responses.append(response)

        self.response = ", ".join(responses)
        self.write({'response': self.response})
        return self.response
    
class CreateContractGroup(models.Model):
    _inherit = 'res.groups'

    @api.model
    def create_contract_group(self):
        # Cria o Grupo
        group = self.env['res.groups'].create({
            'name': 'Gerador de Contratos',
            'category_id': self.env.ref('base.module_category_productivity').id,
        })

        # assina as permissões do grupo no modulo
        model_gerador_de_contratos = self.env['ir.model']._get('gerador_de_contratos.model_gerador_de_contratos')
        model_gerador_de_contratos.write({
            'group_ids': [(4, group.id, 0)],
        })

        return True
    
    def _post_init_hook(cr, registry):
        env = api.Environment(cr, 1, {})
        env['res.groups'].create_contract_group()

class ContractPDFController(http.Controller):
    @http.route('/api/contracts/<int:contract_id>/pdf', type='http', auth='public')
    def get_contract_pdf(self, contract_id):
        contract = request.env['contract.contract'].sudo().browse(contract_id)
        if not contract.exists():
            return "Contract not found"

        pdf_content, _ = request.env.ref('gerador_de_contratos.contract_report').sudo().render_qweb_pdf([contract_id])
        pdfhttpheaders = [('Content-Type', 'application/pdf'),
                          ('Content-Length', len(pdf_content))]
        return request.make_response(pdf_content, headers=pdfhttpheaders)

class ArticleSet(models.Model):
    _name = 'article.set'

    name = fields.Char(string="Nome do Conjunto", required=True)
    articles = fields.Many2many('create.article', string="Artigos", domain="[('type', '=', 'artigo')]")
    descricao = fields.Char(string="Descrição do conjunto", required=True)

    def write(self, vals):
        result = super().write(vals)

        if 'articles' in vals:
            # Busca todos os contratos que contêm o conjunto de artigos alterado
            contracts = self.env['contract.contract'].search([('article_sets', 'in', self.ids)])

            # Atualiza todos os contratos encontrados
            for contract in contracts:
                contract._update_content()

        return result

    def unlink(self):
        contracts = self.env['contract.contract'].search([('article_sets', 'in', self.ids)])

        result = super().unlink()

        for contract in contracts:
            contract._update_content()

        return result

    @api.model
    def create(self, vals):
        new_record = super().create(vals)

        if 'articles' in vals:
            contracts = self.env['contract.contract'].search([('article_sets', 'in', [new_record.id])])

            for contract in contracts:
                contract._update_content()

        return new_record

class ContractContract(models.Model):
    _name = 'contract.contract'

    name = fields.Char(string="Nome", required=True)
    contract_type = fields.Many2many('account.payment.term', 'contract_contract_payment_term_rel', 'contract_id',
                                     'payment_term_id', string="Tipo de Contrato", required=True,
                                     default=lambda self: self._get_default_payment_terms())
    contract_model_id = fields.Many2one(
        'contract.model', string="Modelo de Contrato")
    clause_ids = fields.Many2many('create.article', 'contract_clause_rel', 'contract_id',
                                  'clause_id', string="Clausulas", domain="[('type', '=', 'artigo')]")
    condition_ids = fields.Many2many('create.article', 'contract_condition_rel', 'contract_id',
                                     'condition_id', string="Condições", domain="[('type', '=', 'condição')]")
    article_sets = fields.Many2many(
        'article.set', 'contract_set_article_rel',
        'contract_id', 'article_sets',
        string="Conjuntos de Artigos")
    product_ids = fields.Many2many('product.product',
                                   'contract_product_rel', 
                                   'contract_id', 
                                   'product_id', 
                                   string="Produtos")
    content = fields.Html(string="Conteúdo", required=True)
    
    
    @api.constrains('condition_ids')
    def _check_condition_ids(self):
        for record in self:
            for condition in record.condition_ids:
                if condition.type != 'condição':
                    raise ValidationError("Somente condições podem ser adicionadas no campo de condições. O artigo '%s' não é uma condição." % condition.name)
        
    @api.model
    def _get_default_payment_terms(self):
        payment_terms = self.env['sale.order'].search([]).mapped('payment_term_id')
        return payment_terms.ids
    
    
    def view_article(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Artigos & Condições',
            'res_model': 'create.article',
            'view_mode': 'tree,form',
            'target': 'current',
        }
        
    def view_article_condition(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Condições de Artigo',
            'res_model': 'create.article.condition',
            'view_mode': 'tree,form',
            'target': 'current',
        }
        

    def evaluate_condition(self, condition, sale_id):
        
        """
        Avalia a condição para cada artigo associado a este contrato.

        :param condition: O registro da condição
        :return: Um booleano indicando se a condição foi satisfeita
        :raise ValidationError: Se algum erro ocorrer durante a avaliação da condição
        
        """
        return condition.evaluate_condition(sale_id)
    
            
    def get_sales_contract(self, sale_id, **kwargs):
        # Garantindo acesso de super usuário
        self = self.sudo()

        # Tentativa de encontrar a ordem de venda
        try:
            sale_order = self.env['sale.order'].browse(sale_id)
        except Exception as e:
            _logger.error(f'Erro ao buscar a ordem de venda: {e}')
            return "Erro interno do servidor"

        # Verificando se a ordem de venda existe
        if not sale_order.exists():
            head = {'Tipo-do-Conteudo': 'application/json'}
            body = {"error": "Ordem de venda não encontrada"}
            return {"head": head, "body": body}

        # Recuperando o id do termo de pagamento, se existir
        payment_term_id = sale_order.payment_term_id.id if sale_order.payment_term_id else None

        # Recuperando os ids dos produtos, se existirem, e construindo o product_id no formato desejado
        product_ids = [line.product_id.id for line in sale_order.order_line if line.product_id]

        try:
            contracts = self.env['contract.contract'].search([
                ('contract_type', 'in', payment_term_id),
                ('product_ids', 'in', product_ids)  # <-- ALTERAÇÃO AQUI
            ])
        except Exception as e:
            _logger.error(f'Erro ao buscar o contrato: {e}')
            return "Erro interno do servidor"

        # Verificando se o contrato foi encontrado
        if not contracts:
            head = {'Tipo-do-Conteudo': 'application/json'}
            body = {"error": "Contrato não encontrado"}
            return {"head": head, "body": body}

        # Selecionando o primeiro contrato encontrado
        contract = contracts[0]

        # Lista para armazenar os ids dos artigos a serem removidos
        articles_to_remove = []

        # Criando uma lista para o conteúdo do contrato modificado
        contract_content_list = []
        contract_content_list.append(f'<h1 style="text-align: center"><strong>{contract.name}</strong></h1>')

        # Verificando as condições do contrato e registrando os artigos que devem ser removidos
        for condition in contract.condition_ids:
            articles_to_remove.extend(condition.evaluate_condition(sale_id))

        # Obtendo todos os conjuntos de artigos
        all_article_sets = self.env['article.set'].search([])

        # Construindo o conteúdo modificado do contrato
        for i, article_set in enumerate(all_article_sets):
            clause_number = 1  # Inicializa o número da cláusula para cada conjunto de artigos
            contract_content_list.append(f'<h2 style="text-align: center">{article_set.name.upper()}</h2>')

            for j, article in enumerate(article_set.articles):
                # Fazendo uma cópia do artigo antes das alterações
                article_copy = article.copy()
                
                # Avaliando a condição e modificando a cópia do artigo
                article_copy.evaluate_condition(sale_order.id)

                # Se o id do artigo ORIGINAL estiver na lista de artigos a serem removidos, ignoramos este artigo
                if article.id in articles_to_remove:
                    continue
                    
                # Este artigo deve ser incluído, então adicionamos ao conteúdo
                soup = BeautifulSoup(article_copy.content, 'html.parser')

                for tag in soup.find_all(['p', 'br', 'div']):
                    tag.replace_with(tag.get_text())

                article_content = soup.get_text().strip()
                # Formatação modificada para o formato "Cláusula nª"
                formatted_article_content = f'<p><strong>Cláusula {i+1}.{clause_number}ª</strong>. {article_content}</p>'
                contract_content_list.append(formatted_article_content)
                clause_number += 1  # Incrementa o número da cláusula

        contract_content = "<br/>".join(contract_content_list)

        # Preparando a resposta da requisição
        head = {'Tipo-do-Conteudo': 'application/json'}
        body = {
            'contract_id': contract.id,
            'name': contract.name,
            'content': contract_content,  # Devolvendo a versão modificada do conteúdo
        }
        return {"head": head, "body": body}


    
    def organize_text(self):
        for record in self:
            content = record.content

            if content:  # Verifique se content não está vazio
                # Analisa o conteúdo HTML usando o BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')

                # Encontra todos os elementos <p> e <span> dentro do conteúdo
                paragraphs = soup.find_all('p')
                spans = soup.find_all('span')

                # Remove as tags <p> mantendo o conteúdo entre elas
                for paragraph in paragraphs:
                    # Obtem o conteúdo do parágrafo
                    paragraph_content = paragraph.get_text()
                    # Substitui o parágrafo pelo seu conteúdo
                    paragraph.replace_with(paragraph_content)

                # Remove as tags <span> mantendo o conteúdo entre elas
                for span in spans:
                    # Obtem o conteúdo do span
                    span_content = span.get_text()
                    # Substitui o span pelo seu conteúdo
                    span.replace_with(span_content)
                    
                # Atualiza o conteúdo com as tags <p> e <span> removidas
                record.write({'content': str(soup)})


    def action_organize_text(self):
        self.organize_text()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }    


    @api.model
    def _compute_payment_terms(self):
        payment_terms = self.env['account.payment.term'].search([])
        options = [(str(term.id), term.name) for term in payment_terms]
        return options


    @api.model
    def _get_default_payment_term(self):
        payment_terms = self.env['account.payment.term'].search([])
        if payment_terms:
            return str(payment_terms[0].id)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "O nome do contrato deve ser único."),
    ]


    @api.onchange('clause_ids', 'condition_ids', 'contract_model_id', 'article_sets')
    def _update_content(self):
        contract_content_list = []

        if self.contract_model_id:
            contract_content_list.append(f'<h1 style="text-align: center"><strong>{self.contract_model_id.name}</strong></h1>')
            contract_content_list.append(self.contract_model_id.content)

        # Itera sobre as cláusulas do contrato
        for i, clause in enumerate(self.clause_ids):
            # Analisa o conteúdo da cláusula como HTML
            soup = BeautifulSoup(clause.content, 'html.parser')

            for tag in soup.find_all(['p', 'br', 'div']):
                tag.replace_with(tag.get_text())

            # Obtém o conteúdo da cláusula sem as tags HTML, e remove espaços em branco no início e no final
            clause_content = soup.get_text().strip()

            # Adiciona o conteúdo da cláusula com a formatação desejada, sem as tags <p>
            formatted_clause_content = str("Cláusula.") + str(i+1) + '.' + clause_content
            contract_content_list.append(formatted_clause_content)

        # Itera sobre os conjuntos de artigos
        for i, article_set in enumerate(self.article_sets):
            contract_content_list.append(f'<h2 style="text-align: center">{article_set.name.upper()}</h2>')

            # Itera sobre os artigos no conjunto de artigos
            for j, article in enumerate(article_set.articles):
                # Analisa o conteúdo do artigo como HTML
                soup = BeautifulSoup(article.content, 'html.parser')

                for tag in soup.find_all(['p', 'br', 'div']):
                    tag.replace_with(tag.get_text())

                # Obtém o conteúdo do artigo sem as tags HTML, e remove espaços em branco no início e no final
                article_content = soup.get_text().strip()

                # Adiciona o conteúdo do artigo com a formatação desejada, sem as tags <p>
                formatted_article_content = str("Cláusula.") + str(i+1) + '.' + str(j+1) + '.' + article_content
                contract_content_list.append(formatted_article_content)

        contract_content = "<br/>".join(contract_content_list)
        # Chama a função organize_text() após a criação do conteúdo do contrato
        self.organize_text()

        # Atualiza o conteúdo do contrato
        self.sudo().write({'content': contract_content})

    def write(self, vals):
        result = super().write(vals)
        if any(field in vals for field in ['contract_model_id', 'clause_ids', 'condition_ids', 'article_sets']):
            self._update_content()
        return result


    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._update_content()
        return record
    
    
class CreateArticle(models.Model):
    _name = 'create.article'

    name = fields.Char(string="Nome", required=True)
    description = fields.Text(string="Descrição")
    content = fields.Html(string="Conteúdo")
    type = fields.Selection([('artigo', 'Artigo'), ('condição', 'Condição')], string="Tipo de Artigo", required=True)
    related_clauses = fields.Many2many('create.article', 'related_clauses_rel', 'id', 'clause_id', string="Clausulas Relacionadas", domain="[('type', '=', 'artigo')]")
    condition_ids = fields.Many2many('create.article.condition', string="Condições")
    check_logic = fields.Char(string="Lógica de Verificação")
    action_if_match = fields.Selection([('hide', 'Esconder')], string="Ação se corresponder")
    SPECIAL_VARS = [('PESOCURSO', 'Tipo de uso de tempo'), ('ALUNOCTMAT', 'Taxa de Matrícula'), ('SEXSUF', 'Prefixo de sexo do aluno'), ('ALUNONAC', 'Nacionalidade do aluno'), ('PESOCURSOB', 'Total de horas do curso'), 
                    ('ALUNOCNOME', 'Nome do curso'), ('ALUNOCPARC', 'Valor total do curso'), ('ALUNOCQPARC', 'Quantidade de parcelas'), ('DATACONTRATO', 'Data do contrato'), 
                    ('ALUNONOME', 'Nome do aluno'), ('ALUNOCPF', 'CPF do aluno'), ('ALUNOADDRESS', 'Endereço do aluno'), ('ALUNOCTFONE', 'Telefone do aluno'), 
                    ('ALUNOCTMAIL', 'Email do aluno'), ('VALOR TOTAL', 'Valor total')]
    
    variable = fields.Selection([('amount_total', 'Total'), 
        ('payment_term_id', 'Termo de pagamento'),
        ('date_order', 'Data da ordem'),
        ('sale_order_template_id', 'Modelo de ordem de venda'),
        ('partner_id', 'Parceiro'),
        ('partner_id.name', 'Nome do parceiro'),
        ('partner_id.l10n_br_cnpj_cpf', 'CNPJ/CPF do parceiro'),
        ('partner_id.zip', 'CEP do parceiro'),
        ('partner_id.email', 'Email do parceiro'),
        ('partner_id.phone', 'Telefone do parceiro'),
        ('partner_id.mobile', 'Celular do parceiro'),
        ('partner_id.street', 'Rua do parceiro')] + SPECIAL_VARS, string="Variável")
    
    

    def insert_variable(self):
        # Formata a variável selecionada
        variable_tag = '{{' + self.variable + '}}'

        # Adiciona a variável ao campo content
        self.content = (self.content or '') + ' ' + variable_tag

    def evaluate_condition(self, record_id):
        articles_to_remove = []
        for condition in self.condition_ids:
            result = condition.evaluate_condition(record_id)
            articles_to_remove.extend(result)
        return articles_to_remove

    def write(self, vals):
        result = super().write(vals)

        # Busca todos os conjuntos de artigos que contêm o artigo alterado
        article_sets = self.env['article.set'].search([('articles', 'in', self.ids)])

        # Busca todos os contratos que contêm os conjuntos de artigos encontrados
        contracts = self.env['contract.contract'].search([('article_sets', 'in', article_sets.ids)])

        # Atualiza todos os contratos encontrados
        for contract in contracts:
            contract._update_content()

        return result

class ArticleCondition(models.Model):
    _name = 'create.article.condition'

    article_ids = fields.Many2many('create.article', string="Artigos")
    target_model_id = fields.Many2one('ir.model', string="Modelo Alvo")
    target_field_id = fields.Many2one('ir.model.fields', string="Campo Alvo", domain="[('model_id', '=', target_model_id)]")
    logical_operator = fields.Selection([('==', 'Igual a'), ('!=', 'Diferente de'), ('>', 'Maior que'), ('<', 'Menor que'), ('>=', 'Maior ou igual a'), ('<=', 'Menor ou igual a')], string="Operador Lógico")
    comparison_value = fields.Char(string="Valor de Comparação")

    @api.onchange('target_model_id')
    def _onchange_target_model_id(self):
        if self.target_model_id:
            return {'domain': {'target_field_id': [('model_id', '=', self.target_model_id.id)]}}
        else:
            return {'domain': {'target_field_id': []}}

    def evaluate_condition(self, record_id):
        
        """
        Avalia a condição para cada artigo. Se a condição for satisfeita, 
        adiciona o artigo à lista de artigos a serem removidos.

        :param record_id: O id do registro do modelo alvo
        :return: Uma lista contendo os ids dos artigos cuja condição foi satisfeita
        :raise ValidationError: Se algum erro ocorrer durante a avaliação da condição
        """
        
        _logger.info('self: %s', self)

        articles_to_remove = []

        for article in self.article_ids:

            target_model = self.env[self.target_model_id.model].browse(record_id)
            if not target_model.exists():
                raise ValidationError(f"Modelo Alvo '{self.target_model_id.name}' não encontrado")

            target_field = self.target_field_id.name
            if not hasattr(target_model, target_field):
                raise ValidationError(f"Campo Alvo '{target_field}' não encontrado no modelo '{self.target_model_id.name}'")

            field_value = getattr(target_model, target_field)
            comparison_value = self.comparison_value
            try:
                # Converte a string de comparação para o mesmo tipo do valor do campo
                comparison_value = type(field_value)(comparison_value)
            except ValueError:
                raise ValidationError(f"Valor de Comparação '{self.comparison_value}' não pode ser convertido para o tipo de '{target_field}'")

            if (self.logical_operator == '==' and field_value == comparison_value) or \
                (self.logical_operator == '!=' and field_value != comparison_value) or \
                (self.logical_operator == '>' and field_value > comparison_value) or \
                (self.logical_operator == '<' and field_value < comparison_value) or \
                (self.logical_operator == '>=' and field_value >= comparison_value) or \
                (self.logical_operator == '<=' and field_value <= comparison_value):
                
                # Se a condição for satisfeita, adicionamos o id do artigo à lista de artigos a serem removidos
                articles_to_remove.append(article.id)

        return articles_to_remove

class ContractModel(models.Model):
    _name = 'contract.model'
    name = fields.Char(string="Nome", required=True)
    description = fields.Text(string="Descrição")
    content = fields.Html(string="Conteúdo", required=True)
    SPECIAL_VARS = ['PESOCURSO', 'ALUNOCTMAT', 'SEXSUF', 'ALUNONAC', 'PESOCURSOB', 'ALUNOCNOME', 'ALUNOCPARC', 'ALUNOCQPARC', 'DATACONTRATO', 'ALUNONOME', 'ALUNOCPF', 'ALUNOADDRESS', 'ALUNOCTFONE', 'ALUNOCTMAIL', 'VALOR TOTAL']
    variable = fields.Selection(
            [('amount_total', 'Total'), 
            ('payment_term_id', 'Termo de pagamento'),
            ('date_order', 'Data da ordem'),
            ('sale_order_template_id', 'Modelo de ordem de venda'),
            ('partner_id', 'Parceiro'),
            ('partner_id.name', 'Nome do parceiro'),
            ('partner_id.l10n_br_cnpj_cpf', 'CNPJ/CPF do parceiro'),
            ('partner_id.zip', 'CEP do parceiro'),
            ('partner_id.email', 'Email do parceiro'),
            ('partner_id.phone', 'Telefone do parceiro'),
            ('partner_id.mobile', 'Celular do parceiro'),
            ('partner_id.street', 'Rua do parceiro'),
            ('PESOCURSO', 'Tipo de uso de tempo'),
            ('ALUNOCTMAT', 'Taxa de Matrícula'),
            ('SEXSUF', 'Prefixo de sexo do aluno'),
            ('ALUNONAC', 'Nacionalidade do aluno'),
            ('PESOCURSOB', 'Total de horas do curso'),
            ('ALUNOCNOME', 'Nome do curso'),
            ('ALUNOCPARC', 'Valor total do curso'),
            ('ALUNOCQPARC', 'Quantidade de parcelas'),
            ('DATACONTRATO', 'Data do contrato'),
            ('ALUNONOME', 'Nome do aluno'),
            ('ALUNOCPF', 'CPF do aluno'),
            ('ALUNOADDRESS', 'Endereço do aluno'),
            ('ALUNOCTFONE', 'Telefone do aluno'),
            ('ALUNOCTMAIL', 'Email do aluno'),
            ('VALOR TOTAL', 'Valor total')
            ], string="Variável")

    def insert_variable(self):
        # Formata a variável selecionada
        if self.variable in self.SPECIAL_VARS:
            variable_tag = '[' + self.variable + ']'
        else:
            variable_tag = '{{' + self.variable + '}}'

        # Adiciona a variável ao campo content
        self.content = (self.content or '') + ' ' + variable_tag

    def write(self, vals):
        result = super().write(vals)
        if 'content' in vals:
            contracts = self.env['contract.contract'].search(
                [('contract_model_id', '=', self.id)])
            for contract in contracts:
                contract._update_content()
        return result



class GeradorViews(models.Model):
    _name = 'gerador_views'

    contract_name = fields.Char(string="Nome do Contrato")
    contract_type = fields.Selection(selection='_compute_payment_terms', string="Especificidade",
                                     required=True, default=lambda self: self._get_default_payment_term())
    contract_model_id = fields.Many2one(
        'contract.model', string="Modelo de Contrato")
    article_sets = fields.Many2many(
        'article.set', 'gerador_views_article_set_rel', 'gerador_view_id', 'article_sets',
        string="Conjuntos de Artigos")
    article_ids = fields.Many2many(
        'create.article', 'gerador_article_rel', 'gerador_id', 'article_id', string="Cláusula")
    condition_ids = fields.Many2many(
        'create.article', 'gerador_condition_rel', 'gerador_id', 'condition_id', string="Grupo de Regras")
    content = fields.Html(string="Conteúdo", required=True, compute='_compute_content')

    @api.model
    def _compute_payment_terms(self):
        payment_terms = self.env['account.payment.term'].search([])
        options = [(str(term.id), term.name) for term in payment_terms]
        return options

    @api.model
    def _get_default_payment_term(self):
        payment_terms = self.env['account.payment.term'].search([])
        if payment_terms:
            return str(payment_terms[0].id)

    @api.depends('contract_model_id', 'article_sets')
    def _compute_content(self):
        for record in self:
            record.content = record.generate_contract_content()

    def generate_contract_content(self):
        contract_content = ""
        if self.contract_model_id:
            contract_content += f'<h1 style="text-align: center">{self.contract_model_id.name}</h1>\n'
            contract_content += f'{self.contract_model_id.content}\n'
        for i, article_set in enumerate(self.article_sets):
            contract_content += f'<p style="text-align: center"><strong>{article_set.name.upper()}</strong></p>\n'
            article_paragraphs = []
            for j, article in enumerate(article_set.articles):
                article_paragraphs.append(article.content)
            merged_article = "".join(article_paragraphs)  # Removido o espaço extra
            contract_content += f'<p><strong><span style="white-space: nowrap;">Cláusula.{i+1}</span></strong>. {merged_article}</p>\n'
        return contract_content

    def generate_manual_contract(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gerador de Contratos Manual',
            'res_model': 'gerador_views',
            'view_mode': 'form',
            'view_id': self.env.ref('gerador_de_contratos.gerador_manual_view').id,
            'target': 'new',
        }

    def generate_simplified_contract(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contrato simplificado',
            'res_model': 'generate.simplified.contract',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def view_article_sets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Conjuntos de Artigos',
            'res_model': 'article.set',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def create_article_set(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Novo Conjunto de Artigos',
            'res_model': 'article.set',
            'view_mode': 'form',
            'target': 'current',
        }

    def create_article(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Novo Modelo de Artigo',
            'res_model': 'create.article',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

    def view_article(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Artigos',
            'res_model': 'create.article',
            'view_mode': 'tree,form',
            'target': 'current',
        }
        
    def view_article_condition(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Condições de Artigo',
            'res_model': 'create.article.condition',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def create_contract_model(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Modelos de Contrato',
            'res_model': 'contract.model',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

    def view_contract_model(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Modelos de Contrato',
            'res_model': 'contract.model',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def create_contract(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Criar Contrato',
            'res_model': 'gerador_views',
            'view_mode': 'form',
            'view_id': self.env.ref('gerador_de_contratos.create_contract_view').id,
            'target': 'new',
        }

    def view_contract(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contratos',
            'res_model': 'contract.contract',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def generate_contract(self):
        contract_content_list = []

        # Inclui o conteúdo do modelo de contrato
        if self.contract_model_id:
            # Adiciona o nome do modelo de contrato como título
            contract_content_list.append(f'<h1 style="text-align: center"><strong>{self.contract_model_id.name}</strong></h1>')

            # Adiciona o conteúdo do modelo de contrato
            contract_content_list.append(self.contract_model_id.content)

        # Inclui o conteúdo dos artigos nos conjuntos de artigos
        for i, article_sets in enumerate(self.article_sets):
            # Adiciona o nome do conjunto de artigos como título
            contract_content_list.append(f'<h2 style="text-align: center">{article_set.name.upper()}</h2>')

            # Itera sobre os artigos no conjunto de artigos
            for j, article in enumerate(article_set.articles):
                article_content = str("Cláusula.") + str(i+1) + 'ª.' + str(j+1) + '.' + article.content

        contract_content = "<br/>".join(contract_content_list)
        return contract_content

        # Atualiza o conteúdo do contrato
        self.sudo().write({'content': contract_content})

        contract = self.env['contract.contract'].create({
            'name': self.contract_name,
            'contract_type': self.contract_type,
            'article_sets': [(6, 0, self.article_sets and self.article_sets.ids or [])],
            'clause_ids': [(6, 0, self.article_ids.ids)],
            'condition_ids': [(6, 0, self.condition_ids.ids)],
            'contract_model_id': self.contract_model_id.id,
            'content': contract_content,
        })
        # Update the content of the contract
        contract._update_content()
        # Call the organize_text function after the contract is created
        contract.organize_text()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contrato Criado',
            'res_model': 'contract.contract',
            'view_mode': 'form',
            'res_id': contract.id,
            'target': 'current',
        }