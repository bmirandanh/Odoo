from odoo import _, api, fields, models
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
from bs4 import BeautifulSoup
from lxml import etree

_logger = logging.getLogger(__name__)


class GenerateSimplifiedContract(models.Model):
    _name = 'generate.simplified.contract'

    # Definindo campos do modelo
    ia_nome = fields.Text(string='Nome do contrato')
    prompt = fields.Text(string='Prompt')
    response = fields.Html(string='Response')
    article_set_ids = fields.Many2many('article.set', string="Conjuntos de Artigos") 
    article_ids = fields.Many2many('create.article', string="Artigos")  
    contract_model_id = fields.Many2one('contract.model', string="Modelo de Contrato") 
    ia_product_ids = fields.Many2many('product.product',
                                   'generate_simplified_contract_product_rel',
                                   'contract_id', 
                                   'product_id',
                                   string="Produtos")
    ia_contract_type = fields.Many2many('account.payment.term', 'generate_simplified_contract_payment_term_rel', 'contract_id',
                                     'payment_term_id', string="Tipo de Contrato", required=True,
                                     default=lambda self: self._get_default_payment_terms())
        
    # Definindo constantes
    MAX_ARTICLES_PER_BATCH = 5
    MAX_TOKENS_PER_ARTICLE = 500
    
    def change_payment_term_field(self):
        for record in self:
            for payment_term in record.ia_contract_type:
                payment_term.field_name = new_value

    @api.model
    def _get_default_payment_terms(self):
        payment_terms = self.env['sale.order'].search([]).mapped('payment_term_id')
        return payment_terms.ids
    
    # Gerar contrato através do auxiliador da IA
    def button_generate_contract_ia(self):
        self.ensure_one()
        self.env['contract.contract'].create({
            'name': self.ia_nome,
            'content': "",
            'contract_type': [(6, 0, self.ia_contract_type.ids)],
            'contract_model_id': self.contract_model_id.id,
            'article_sets': [(6, 0, self.article_set_ids.ids)],
            'product_ids': [(6, 0, self.ia_product_ids.ids)],
        })
        return {'type': 'ir.actions.act_window_close'}
      
    

    def button_create_article_sets(self):
        # Abra o assistente para criar o conjunto de artigos
        return {
            'name': 'Criar Conjunto de Artigos',
            'type': 'ir.actions.act_window',
            'res_model': 'create.article.set.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    # Função para limpar o conteúdo HTML de strings indesejadas
    def clean_html_content(self, html_content):
        # Criando um objeto BeautifulSoup para manipular o conteúdo HTML
        soup = BeautifulSoup(html_content, "html.parser")
        # Extraindo o texto do conteúdo HTML
        text = soup.get_text()

        # Lista de strings indesejadas
        unwanted_strings = [
            "</p>", "\\xa", "<td colspan=\"4\">", "xa0", "\xa0", "<p>", "<strong>", "</strong>", "</p>", "</td>", 
            "\\", "</tr>", "</blockquote>", "_________________________________________________", "<br />", "|", "<br", 
            '<p style="text-align: center">'
        ]

        # Substituindo as strings indesejadas por vazio ''
        for s in unwanted_strings:
            text = text.replace(s, '')

        # Usando expressões regulares para substituir vários espaços por um único espaço
        text = re.sub(' +', ' ', text)

        return text  # Retornando o texto limpo

    # Função para fazer uma requisição à API GPT-3
    def make_gpt3_request(self, prompt):
        # Configurando a chave da API
        openai.api_key = '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'

        try:
            # Fazendo a requisição à API
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature=0.16,
                max_tokens=256,
                top_p=1,
                frequency_penalty=2,
                presence_penalty=2
            )
            return response['choices'][0]['text']
        except Exception as e:
            return str(e) # Retornando a exceção como string

     # Função para criar os prompts
    def create_prompts(self):
        # Buscando os artigos
        articles = self.env['create.article'].search([])

        # Dividindo os artigos em lotes
        batches = [articles[i:i+self.MAX_ARTICLES_PER_BATCH] for i in range(0, len(articles), self.MAX_ARTICLES_PER_BATCH)]
        prompts = []

        # Para cada lote, criar os prompts
        for batch in batches:
            batch_prompts = ["Para cada artigos de contratos, temos códigos únicos. Vou te apresentar nossos artigos, seus códigos únicos e a descrição do seu tipo, analise, pois farei uma pergunta sobre eles logo após: "]
            for article in batch:
                content = self.clean_html_content(article.content)  # limpa o conteúdo HTML com a função
                if len(content.split()) <= self.MAX_TOKENS_PER_ARTICLE:
                    prompt = {"prompt": content, "completion": article.id, "descrição": article.description},  # usa o conteúdo apenas com as informações nescessárias
                    batch_prompts.append(str(prompt))
            batch_prompts.append("Considerando a conversa até aqui, Traga o (ou os) código(s) único(s) dos campos de completion, um ou mais artigo(s), mas apenas os que aborde(m): "+self.prompt+", Formate a resposta entre tags [ANSTART]RESPOSTA[ANEND] conforme o exemplo [ANSTART]CODIGO1,CODIGO2,CODIGO3,...[ANEND], lembrando, apenas os artigos que tenha "+self.prompt+", se não houver nenhum, escreva 'N/D', não coloque nenhum completion, que não possua o tema, é a regra que deve sempre seguir, apenas artigos do solicitado, que foi o tema "+self.prompt+", com este tema, pegue os artigos para a criação de um contrato completo com o que foi analisado: ")
            prompts.append(' '.join(batch_prompts))
        return prompts # Retornando os prompts

    # Função para gerar o contrato
    def button_generate_contract(self):
        # Criando os prompts
        prompts = self.create_prompts()

        responses = []
        article_ids = []
        # Para cada prompt, fazer a requisição à API GPT-3 e armazenar a resposta
        for prompt in prompts:
            response = self.make_gpt3_request(prompt)
            responses.append(response)

            # Extrair os IDs dos artigos da resposta
            ids = re.findall(r'\[ANSTART\](.*?)\[ANEND\]', response)
            for id_str in ids:
                # Separar os IDs por vírgulas e convertê-los para inteiros
                for id in id_str.split(','):
                    try:
                        article_ids.append(int(id))
                    except ValueError:
                        pass  # Ignorar qualquer coisa que não seja um número

        # Unindo as respostas e armazenando no campo 'response'
        self.response = ", ".join(responses)
        self.write({'response': self.response})

        # Atualizar o campo 'article_ids'
        self.write({'article_ids': [(6, 0, article_ids)]})

        return self.response  # Retornando a resposta
    
    #Botão para chamar o wizard de criação de cláusulas de forma mais prática a resposta do prompt
    def button_create_article_sets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'create.article.set.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id}
        }
        

    def write(self, vals):
        result = super(GenerateSimplifiedContract, self).write(vals)

        if 'article_ids' in vals:
            # Busca todos os contratos que contêm o conjunto de artigos alterado
            contracts = self.env['contract.contract'].search([('article_sets', 'in', self.ids)])

            # Atualiza todos os contratos encontrados
            for contract in contracts:
                contract._update_content()

        return result

    def unlink(self):
        contracts = self.env['contract.contract'].search([('article_sets', 'in', self.ids)])

        result = super(GenerateSimplifiedContract, self).unlink()

        for contract in contracts:
            contract._update_content()

        return result

    @api.model
    def create(self, vals):
        new_record = super(GenerateSimplifiedContract, self).create(vals)

        if 'article_ids' in vals:
            contracts = self.env['contract.contract'].search([('article_sets', 'in', [new_record.id])])

            for contract in contracts:
                contract._update_content()

        return new_record
    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    def open_action(self):
        # Obtenha todos os pedidos de venda relacionados a este parceiro
        sale_orders = self.env['sale.order'].search([('partner_id', '=', self.id)])
        
        # Atualize o campo rest_contract para True para todos esses pedidos de venda
        sale_orders.write({'rest_contract': True})

        # Determinar qual visão usar com base no grupo de usuários
        user = self.env.user
        if user.has_group('gerador_de_contratos.access_gerador_de_contratos') or user.has_group('base.group_system'):
            form_view_id = self.env.ref('gerador_de_contratos.view_order_form_special').id
        else:
            form_view_id = self.env.ref('gerador_de_contratos.view_order_form_regular').id

        self.ensure_one()
        return {
            'name': _('Sales Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('sale.view_order_tree').id, 'tree'), (form_view_id, 'form')],
            'domain': [('partner_id', '=', self.id)],
            'context': {'search_default_partner_id': self.id, 'default_partner_id': self.id, 'edit': True, 'create': False},
            'target': 'current'
        }

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Campo que relaciona a ordem de venda com suas versões de contrato.
    contract_version_ids = fields.One2many(
        'sale.order.contract.version', 'sale_order_id', string='Versões do Contrato'
    )
    rest_contract = fields.Boolean(string="Rest Contract", default=False)
    show_contract_versions = fields.Boolean(string="Mostrar versões do contrato", default=False)
    

class SaleOrderContractVersion(models.Model):
    _name = 'sale.order.contract.version'
    _description = 'Versão do Contrato da Ordem de Venda'

    # Campo que relaciona a versão do contrato com a ordem de venda.
    sale_order_id = fields.Many2one(
        'sale.order', 
        string='Ordem de Venda Relacionada', 
        ondelete='cascade'  # Escolha o comportamento desejado ao deletar.
    )
    name = fields.Char(string='Nome da Versão')
    texto_html_contrato = fields.Html(string='Conteúdo do Contrato')
    data_contrato = fields.Datetime(string='Data do Contrato')
    version_number = fields.Integer(string='Número da Versão')

    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sale_order_id = vals.get('sale_order_id')
            sale_order = self.env['sale.order'].browse(sale_order_id)
            # Pega o número da última versão e adiciona 1
            last_version = max(sale_order.contract_version_ids.mapped('version_number'), default=0)
            vals['version_number'] = last_version + 1
        return super(SaleOrderContractVersion, self).create(vals_list)
    
        
class ArticleWizardRel(models.TransientModel):
    _name = 'article.wizard.rel'
    
    wizard_id = fields.Many2one('create.article.set.wizard', ondelete='cascade')
    article_id = fields.Many2one('create.article')
    selected = fields.Boolean()
    article_name = fields.Char(related='article_id.name', string="Article Name", readonly=True)
    article_description = fields.Text(related='article_id.description', string="Article Description", readonly=True)
    article_content = fields.Html(related='article_id.content', string="Article Content", readonly=True)


class CreateArticleSetWizard(models.TransientModel):
    _name = 'create.article.set.wizard'

    name = fields.Char(string='Nome do Conjunto')
    descricao = fields.Char(string='Descrição do conjunto')
    contract_id = fields.Many2one('generate.simplified.contract', string="Contrato", required=True)
    article_set_id = fields.Many2one('article.set', string="Conjunto de Artigos")
    article_ids = fields.One2many(
        'article.wizard.rel', 
        'wizard_id',
        string="Artigos selecionados pela IA")
    selected_articles_ids = fields.Many2many('create.article', string="Artigos a adicionar", compute="_compute_selected_articles")

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        if self.contract_id:
            ArticleWizardRel = self.env['article.wizard.rel']
            rels = ArticleWizardRel.search([('wizard_id', '=', self.id)])
            rels.unlink()

            for article in self.contract_id.article_ids:
                ArticleWizardRel.create({'wizard_id': self.id, 'article_id': article.id, 'selected': False})

    @api.depends('article_ids.selected')
    def _compute_selected_articles(self):
        for record in self:
            record.selected_articles_ids = record.article_ids.filtered(lambda r: r.selected).mapped('article_id')

    def button_create_article_set(self):
        self.ensure_one()
        articles = self.selected_articles_ids
        self.env['article.set'].create({
            'name': self.name,
            'descricao': self.descricao,
            'articles': [(6, 0, articles.ids)]
        })
        return {'type': 'ir.actions.act_window_close'}
    
    
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
            return {"head": {'Tipo-do-Conteudo': 'application/json'}, "body": {"error": "Erro interno do servidor"}}

        # Verificando se a ordem de venda existe
        if not sale_order.exists():
            return {"head": {'Tipo-do-Conteudo': 'application/json'}, "body": {"error": "Ordem de venda não encontrada"}}

        # Recuperando o id do termo de pagamento, se existir
        payment_term_id = sale_order.payment_term_id.id if sale_order.payment_term_id else None

        # Recuperando os ids dos produtos, se existirem, e construindo o product_id no formato desejado
        product_ids = [line.product_id.id for line in sale_order.order_line if line.product_id]

        try:
            contract = self.env['contract.contract'].search([
                ('contract_type', 'in', [payment_term_id]),
                ('product_ids', 'in', product_ids)  
            ], limit=1)  # Adicionando limit=1 para pegar somente um contrato
        except Exception as e:
            _logger.error(f'Erro ao buscar o contrato: {e}')
            return {"head": {'Tipo-do-Conteudo': 'application/json'}, "body": {"error": "Erro interno do servidor"}}

        # Verificando se o contrato foi encontrado
        if not contract:
            return {"head": {'Tipo-do-Conteudo': 'application/json'}, "body": {"error": "Contrato não encontrado"}}

        # Se o contrato possuir o campo contract_model_id, obtenha o content
        contract_model_content = contract.contract_model_id.content if hasattr(contract, 'contract_model_id') and contract.contract_model_id else None                      

        # Criando uma lista para o conteúdo do contrato modificado
        contract_content_list = []
        contract_content_list.append(f'<h1 style="text-align: center"><strong>{contract.name}</strong></h1>')
        
        # Se o contrato possuir o campo contract_model_id, obtenha o content
        if hasattr(contract, 'contract_model_id') and contract.contract_model_id:
            contract_model_content = contract.contract_model_id.content
            contract_content_list.append(contract_model_content)

        articles_to_remove = []
        # Verificando as condições do contrato e registrando os artigos que devem ser removidos
        for condition in contract.condition_ids:
            articles_to_remove.extend(condition.evaluate_condition(sale_id))

        # Obtendo conjuntos de artigos/cláusulas para o contrato escolhido
        article_sets_for_contract = contract.article_sets

        # Construindo o conteúdo modificado do contrato
        for i, article_set in enumerate(article_sets_for_contract):
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
                        
                soup = BeautifulSoup(article_copy.content, 'html.parser')

                for tag in soup.find_all(['p', 'br', 'div']):
                    tag.replace_with(tag.get_text())

                article_content = soup.get_text().strip()

                if clause_number >= 2:
                    formatted_article_content = f'<p><strong>§{clause_number}º</strong> {article_content}</p>'
                    contract_content_list.append(formatted_article_content)
                    clause_number += 1 
                else:
                    formatted_article_content = f'<p><strong>Cláusula {i+1}.{clause_number}ª</strong>. {article_content}</p>'
                    contract_content_list.append(formatted_article_content)
                    clause_number += 1  # Incrementa o número da cláusula

        contract_content = "<br/>".join(contract_content_list)

        ############### Obtendo valores das variáveis: ###############
        
        # Obtenha os valores do campo course_itrn_time_id de todos os itens de pedido
        course_values = [line.product_id.course_itrn_time_id for line in sale_order.order_line if hasattr(line.product_id, 'course_itrn_time_id')]
        # Obtenha os valores do campo course_base_time_id de todos os itens de pedido
        base_course_values = [line.product_id.course_base_time_id for line in sale_order.order_line if hasattr(line.product_id, 'course_base_time_id')]
        # Obtenha os nomes de todos os produtos do item de pedido
        product_names = [line.product_id.name for line in sale_order.order_line if hasattr(line.product_id, 'name')]
        
        
        # Obtenha o valor total da compra
        amount_total_value = str(sale_order.amount_total)
        # obtenha o nome do campo payment_term_id:
        payment_term_name = sale_order.payment_term_id.name
        # obtenha o valor do campo date_order
        contract_date = sale_order.date_order
        # data no formato "dd/mm/yyyy"
        formatted_contract_date = contract_date.strftime('%d/%m/%Y')
        # obtenha o valor do campo name de partner_id
        client_name = sale_order.partner_id.name
        
        
        ## Taxa de Matrícula
        # Definindo os códigos padrão a serem pesquisados
        default_codes_to_search = ['MATRICULA', 'MATRICULA-BOLETO', 'MATRICULA-PIX']
        # Procurando a linha do pedido de venda que corresponde a um dos códigos padrão
        matriculation_line = self.env['sale.order.line'].search([
            ('order_id', '=', sale_order.id), 
            ('product_id.default_code', 'in', default_codes_to_search)], 
            limit=1  # Busca apenas a primeira correspondência
        )
        # Obtendo o valor do campo price_unit se a linha correspondente for encontrada
        tax_mat = matriculation_line.price_unit if matriculation_line else 0
       
       
        # o campo partner_id da ordem de venda sendo a referência para res.partner
        partner = sale_order.partner_id
        # Obtendo o valor de country_origin_id
        country_name = partner.country_origin_id.name
        # Obtenha o valor de l10n_br_cnpj_cpf
        cpf_value = partner.l10n_br_cnpj_cpf
        # Obtenha os componentes do endereço
        # CEP
        cep = partner.zip or ""
        # Rua
        street = partner.street or ""
        # Complementos
        street2 = partner.street2 or " n/d"
        # Número
        number = partner.l10n_br_number or ""
        # Bairro
        district = partner.l10n_br_district or ""
        # Cidade
        city = partner.city_id.name or ""
        # Estado
        state = partner.state_id.name or ""
        # País
        country = partner.country_id.name or ""
        # Telefone do cliente
        mobile_contract = partner.mobile or ""
        # Celular do cliente
        mobile_contract = partner.mobile or ""
        # Celular do cliente
        phone_contract = partner.phone or ""
        # E-mail do cliente
        email = partner.email or ""
        


        ############### Concatenando os valores das variáveis: ###############
        
        # Concatene os valores course_values
        course_values_str = ", ".join(map(str, course_values))
        # Concatene os valores de base_course_values
        base_course_values_str = ", ".join(map(str, base_course_values))
        # Concatene os nomes
        product_names_str = ", ".join(product_names)
        # Combine os componentes em uma representação de endereço
        address_representation = f"{street} - {street2}, {number}, {district}, {city} - {state}, {country}"


        ############### Substituindo os valores das variáveis: ###############
        
        # Substitua todas as ocorrências de [PESOCURSO] no contract_content pela string concatenada
        contract_content = contract_content.replace("[PESOCURSO]", course_values_str)
        # Substitua todas as ocorrências de [PESOCURSOB] no contract_content pela string concatenada
        contract_content = contract_content.replace("[PESOCURSOB]", base_course_values_str)
        #Substitua todas as ocorrências de [ALUNOCNOME] no contract_content pela string concatenada
        contract_content = contract_content.replace("[ALUNOCNOME]", product_names_str)
        # Substitua todas as ocorrências de [ALUNONAC] no contract_content pelo nome do país
        contract_content = contract_content.replace("[ALUNONAC]", country_name)
        # Substitua todas as ocorrências de [ALUNOCPF] no contract_content pelo CPF
        contract_content = contract_content.replace("[ALUNOCPF]", cpf_value)
        # Substitua todas as ocorrências de [ALUNOCPF] no contract_content endereço completo
        contract_content = contract_content.replace("[ALUNOADDRESS]", address_representation)
        # Substitua todas as ocorrências de [ALUNOCTFONE] no contract_content pelo telefone móvel
        contract_content = contract_content.replace("[ALUNOCTFONE]", mobile_contract)
        # Substitua todas as ocorrências de [ALUNOCTMAIL] no contract_content pelo e-mail
        contract_content = contract_content.replace("[ALUNOCTMAIL]", email)
        # Substitua todas as ocorrências de [ALUNOCPARC] no contract_content pelo valor total
        contract_content = contract_content.replace("[ALUNOCPARC]", amount_total_value)
        # Substitua todas as ocorrências de "[ALUNOCQPARC]" no contract_content pelo nome das condições de pagamento
        contract_content = contract_content.replace("[ALUNOCQPARC]", payment_term_name)
        # Substitua todas as ocorrências de "[DATACONTRATO]" no contract_content pela data formatada
        contract_content = contract_content.replace("[DATACONTRATO]", formatted_contract_date)
        # Substitua todas as ocorrências de "[DATA]" no contract_content pela data formatada
        contract_content = contract_content.replace("[DATA]", formatted_contract_date)
        # Substitua todas as ocorrências de "[ALUNONOME]" no contract_content pelo nome do cliente
        contract_content = contract_content.replace("[ALUNONOME]", client_name)
        # Substitua todas as ocorrências de [VALOR TOTAL] no contract_content pelo valor total
        contract_content = contract_content.replace("[VALOR TOTAL]", amount_total_value)
        # Substitua todas as ocorrências de [VALORTOTAL] no contract_content pelo valor total
        contract_content = contract_content.replace("[VALORTOTAL]", amount_total_value)
        # Substitua todas as ocorrências de [TOTALVALUE] no contract_content pelo valor total
        contract_content = contract_content.replace("[TOTALVALUE]", amount_total_value)
        # Substitua todas as ocorrências de [amount_total] no contract_content pelo valor total
        contract_content = contract_content.replace("[amount_total]", amount_total_value)
        # Substitua todas as ocorrências de "[payment_term_id]" no contract_content pelo nome das condições de pagamento
        contract_content = contract_content.replace("[payment_term_id]", payment_term_name)
        # Substitua todas as ocorrências de "[date_order]" no contract_content pela data formatada
        contract_content = contract_content.replace("[date_order]", formatted_contract_date)
        # Substitua todas as ocorrências de "[partner_id.name]" no contract_content pelo nome do cliente
        contract_content = contract_content.replace("[partner_id.name]", client_name)
        # Substitua todas as ocorrências de [partner_id.l10n_br_cnpj_cpf] no contract_content pelo CPF
        contract_content = contract_content.replace("[partner_id.l10n_br_cnpj_cpf]", cpf_value)
        # Substitua todas as ocorrências de [partner_id.zip] no contract_content pelo CEP
        contract_content = contract_content.replace("[partner_id.zip]", cep)
        # Substitua todas as ocorrências de [partner_id.email] no contract_content pelo Email
        contract_content = contract_content.replace("[partner_id.email]", email)
        # Substitua todas as ocorrências de [partner_id.mobile] no contract_content pelo Celular
        contract_content = contract_content.replace("[partner_id.mobile]", mobile_contract)
        # Substitua todas as ocorrências de [partner_id.phone] no contract_content pelo Telefone
        contract_content = contract_content.replace("[partner_id.phone]", phone_contract)
        # Substitua todas as ocorrências de [partner_id.street] no contract_content pela Rua
        contract_content = contract_content.replace("[partner_id.street]", street)
        # Substitua todas as ocorrências de [ALUNOCTMAT] no contract_content pela Taxa de matrícula
        contract_content = contract_content.replace("[ALUNOCTMAT]", str(tax_mat))
        
        # Preparando a resposta da requisição
        head = {'Tipo-do-Conteudo': 'application/json'}

        body = {
            'contract_id': contract.id,
            'name': contract.name,
            'content': contract_content,  # Devolvendo a versão modificada do conteúdo
        }
        
        # Criando uma nova entrada para a versão do contrato
        self.env['sale.order.contract.version'].create({
            'sale_order_id': sale_order.id,  # Associando à ordem de venda
            'name': contract.name,
            'texto_html_contrato': contract_content,
            'data_contrato': fields.Datetime.now()
        })
        
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
        clause_number = 1  # Inicializamos o número da cláusula

        if self.contract_model_id:
            contract_content_list.append(f'<h1 style="text-align: center"><strong>{self.contract_model_id.name}</strong></h1>')
            contract_content_list.append(self.contract_model_id.content)

        # Itera sobre as cláusulas do contrato
        for i, clause in enumerate(self.clause_ids):
            soup = BeautifulSoup(clause.content, 'html.parser')

            for tag in soup.find_all(['p', 'br', 'div']):
                tag.replace_with(tag.get_text())

            clause_content = soup.get_text().strip()

            # Utilizando a nova lógica de formatação para as cláusulas
            if clause_number >= 2:
                formatted_clause_content = f'<p><strong>§{clause_number}º</strong> {clause_content}</p>'
                contract_content_list.append(formatted_clause_content)
            else:
                formatted_clause_content = f'<p><strong>Cláusula {i+1}.{clause_number}ª</strong>. {clause_content}</p>'
                contract_content_list.append(formatted_clause_content)
            clause_number += 1

        # Itera sobre os conjuntos de artigos
        for i, article_set in enumerate(self.article_sets):
            contract_content_list.append(f'<h2 style="text-align: center">{article_set.name.upper()}</h2>')

            # Reinicializa a numeração das cláusulas para cada novo conjunto de artigos
            clause_number = 1

            for j, article in enumerate(article_set.articles):
                soup = BeautifulSoup(article.content, 'html.parser')

                for tag in soup.find_all(['p', 'br', 'div']):
                    tag.replace_with(tag.get_text())

                article_content = soup.get_text().strip()

                # Utilizando a nova lógica de formatação para os artigos
                if clause_number >= 2:
                    formatted_article_content = f'<p><strong>§{clause_number}º</strong> {article_content}</p>'
                    contract_content_list.append(formatted_article_content)
                else:
                    formatted_article_content = f'<p><strong>Cláusula {i+1}.{clause_number}ª</strong>. {article_content}</p>'
                    contract_content_list.append(formatted_article_content)
                clause_number += 1

        contract_content = "<br/>".join(contract_content_list)
        self.organize_text()
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
    temp_select = fields.Boolean(string="Selecionar", default=False)  ,
    SPECIAL_VARS = [('PESOCURSO', 'Tipo de uso de tempo'), ('ALUNOCTMAT', 'Taxa de Matrícula'), ('SEXSUF', 'Prefixo de sexo do aluno'), ('ALUNONAC', 'Nacionalidade do aluno'), ('PESOCURSOB', 'Total de horas do curso'), 
                    ('ALUNOCNOME', 'Nome do curso'), ('ALUNOCPARC', 'Valor total do curso'), ('ALUNOCQPARC', 'Quantidade de parcelas'), ('DATACONTRATO', 'Data do contrato'), 
                    ('ALUNONOME', 'Nome do aluno'), ('ALUNOCPF', 'CPF do aluno'), ('ALUNOADDRESS', 'Endereço do aluno'), ('ALUNOCTFONE', 'Telefone do aluno'), 
                    ('ALUNOCTMAIL', 'Email do aluno'), ('VALOR TOTAL', 'Valor total')]
    
    variable = fields.Selection([('amount_total', 'Total'), 
        ('payment_term_id', 'Termo de pagamento'),
        ('date_order', 'Data da ordem'),
        ('partner_id.name', 'Nome do parceiro'),
        ('partner_id.l10n_br_cnpj_cpf', 'CNPJ/CPF do parceiro'),
        ('partner_id.zip', 'CEP do parceiro'),
        ('partner_id.email', 'Email do parceiro'),
        ('partner_id.phone', 'Telefone do parceiro'),
        ('partner_id.mobile', 'Celular do parceiro'),
        ('partner_id.street', 'Rua do parceiro')] + SPECIAL_VARS, string="Variável")
    

    def insert_variable(self):
        # Formata a variável selecionada
        variable_tag = '[' + self.variable + ']'

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
            variable_tag = '[' + self.variable + ']'

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
        clause_number = 1  # Inicializando a variável de contagem de cláusula
        for i, article_set in enumerate(self.article_sets):
            contract_content += f'<p style="text-align: center"><strong>{article_set.name.upper()}</strong></p>\n'
            article_paragraphs = []
            for j, article in enumerate(article_set.articles):
                article_content = article.content  # Captura o conteúdo do artigo
                # Aplicando a lógica de formatação
                if clause_number >= 2:
                    formatted_article_content = f'<p><strong>§{clause_number}º</strong> {article_content}</p>'
                else:
                    formatted_article_content = f'<p><strong>Cláusula {i+1}.{clause_number}ª</strong>. {article_content}</p>'
                article_paragraphs.append(formatted_article_content)
                clause_number += 1  # Incrementa a contagem de cláusula
            merged_article = "".join(article_paragraphs)
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
        for i, article_set in enumerate(self.article_sets):
            clause_number = 1  # Reinicializando a variável de contagem de cláusula para cada conjunto de artigos
            
            # Adiciona o nome do conjunto de artigos como título
            contract_content_list.append(f'<h2 style="text-align: center">{article_set.name.upper()}</h2>')

            # Itera sobre os artigos no conjunto de artigos
            for j, article in enumerate(article_set.articles):
                article_content = article.content  # Captura o conteúdo do artigo

                # Aplicando a lógica de formatação
                if clause_number >= 2:
                    formatted_article_content = f'<p><strong>§{clause_number}º</strong> {article_content}</p>'
                else:
                    formatted_article_content = f'<p><strong>Cláusula {i+1}.{clause_number}ª</strong>. {article_content}</p>'
                contract_content_list.append(formatted_article_content)

                clause_number += 1  # Incrementa a contagem de cláusula

        contract_content = "<br/>".join(contract_content_list)
        
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
