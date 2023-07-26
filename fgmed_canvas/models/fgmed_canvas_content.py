# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo import http
from odoo.http import request

class FgmedCanvasSearch(http.Controller):

    @http.route(['/api/fgmed/canvas/search'], type='json', auth='user', methods=['POST'])
    def canvas_search(self, **payload):
        search_value = payload.get('search_value', None)
        if not search_value:
            return {"error": "Search value not provided"}

        # Buscar os modelos que referenciam o valor de busca
        model_to_search = ['fgmed.canvas.content'] # adicione outros modelos conforme necessário
        results = {}

        for model_name in model_to_search:
            model = request.env[model_name]
            # Aqui supõe-se que o valor de busca pode ser encontrado nos campos 'name', 'description' ou 'tags_ids.name'
            records = model.search(['|', '|', ('name', '=', search_value), ('description', '=', search_value), ('tags_ids.name', '=', search_value)])

            # Preparar os dados para a resposta
            results[model_name] = []
            for rec in records:
                results[model_name].append({
                    'id': rec.id,
                    'name': rec.name,
                    'canvas_id': rec.canvas_id,
                    'canvas_secode': rec.canvas_secode,
                    'unique': rec.unique,
                    'description': rec.description,
                    'total_time': rec.total_time,
                    'custom_title': rec.custom_title,
                    'thumbnail': rec.thumbnail,
                    'content_type': rec.content_type.id if rec.content_type else False,
                    'author_ids': [author.id for author in rec.author_ids],
                    'tags_ids': [tag.id for tag in rec.tags_ids]
                    # adicione outros campos conforme necessário
                })

        return results

class FgmedCanvasContent(models.Model):
    _name = "fgmed.canvas.content"
    _description = 'Organiza os conteúdos disponíveis no Canvas'

    name = fields.Char(string='Nome do conteúdo')
    canvas_id = fields.Integer(string='Id do conteúdo no Canvas - id')
    canvas_secode = fields.Char(string='Código de incrição - self_enrollment_code')
    unique = fields.Char(string='Código identificador do conteúdo no Canvas - uuid')
    description = fields.Char(string='Descrição do conteúdo')
    total_time = fields.Integer(string='Duração total do conteúdo')
    custom_title = fields.Char(string='Título estilizado do conteúdo')
    thumbnail = fields.Char(string='Thumbnail do conteúdo')
    content_type = fields.Many2one('fgmed.canvas.content.type', string='Tipo de conteúdo')
    author_ids = fields.Many2many('fgmed.canvas.authors', string='Autores')
    tags_ids = fields.Many2many('fgmed.canvas.content.tags', string='Tags')

class FgmedCanvasUsers(models.Model):
    _name = "fgmed.canvas.users"
    _description = 'Contém uma lista de usuários do canvas'

    user_id = fields.Integer(string='ID do usuário')
    user_uuid = fields.Char(string='Hash do Usuário')


class FgmedCanvasContentType(models.Model):
    _name = "fgmed.canvas.content.type"
    _description = 'Permite categorizar por tipo, os conteúdos do canvas'

    name = fields.Char(string='Nome')


class FgmedCanvasAuthor(models.Model):
    _name = "fgmed.canvas.authors"
    _description = 'Permite administrar autores dos conteúdos do canvas'

    name = fields.Char(string='Nome')
    content_ids = fields.Many2many('fgmed.canvas.content', string='Conteúdos do autor')


class FgmedCanvasContentViews(models.Model):
    _name = "fgmed.canvas.content.views"
    _description = 'Permite administrar visualizações dos conteúdos'

    cv_content_id = fields.Many2one('fgmed.canvas.content', string='Curso', required=True)
    cv_user_id = fields.Many2one('fgmed.canvas.users', string='Usuário', required=True)


class FgmedCanvasContentInteraction(models.Model):
    _name = "fgmed.canvas.content.interactions"
    _description = 'Permite administrar interações nos conteúdos do canvas'

    cv_content_id = fields.Many2one('fgmed.canvas.content', string='Curso', required=True)
    cv_user_id = fields.Many2one('fgmed.canvas.users', string='Usuário', required=True)
    type = fields.Selection([('like', 'Like'),('dislike', 'Dislike'),('super-like', 'Super Like')], string="Tipo de interação", required=True)


class FgmedCanvasContentTime(models.Model):
    _name = "fgmed.canvas.content.times"
    _description = 'Tempo utilizado em um recurso de acordo com cada usuário'

    spent_time = fields.Integer(string='Tempo consumido', required=True)
    cv_content_id = fields.Many2one('fgmed.canvas.content', string='Curso', required=True)
    cv_user_id = fields.Many2one('fgmed.canvas.users', string='Usuário', required=True)


class FgmedCanvasContentTags(models.Model):
    _name = "fgmed.canvas.content.tags"
    _description = 'Permite atribuir tags aos conteúdos'

    name = fields.Char(string="Nome da tag")
    parent_path = fields.Char(index=True)
    parent_id = fields.Many2one('fgmed.canvas.content.tags', 'Tags superiores', ondelete='restrict')
    child_ids = fields.One2many('fgmed.canvas.content.tags', 'parent_id','Subtags')
    cv_content_ids = fields.Many2many('fgmed.canvas.content', string='Conteúdos com a Tag')


class FgmedCanvasEspecialidades(models.Model):
    _name = "fgmed.canvas.courses"
    _description = 'Permite administrar especialidades disponíveis aos assinantes'

    name = fields.Char(string='Nome')
    image = fields.Char(string='Imagem')
    disciplina_ids = fields.Many2many('fgmed.canvas.modules', string='Disciplinas relacionadas')


class FgmedCanvasDisciplinas(models.Model):
    _name = "fgmed.canvas.modules"
    _description = 'Contém as disciplinas das especialidades disponíveis'

    name = fields.Char(string='Nome')
    image = fields.Char(string='Imagem')
    especialidade_ids = fields.Many2many('fgmed.canvas.courses', string='Especialidades relacionadas')
    cv_aulas_content_ids = fields.Many2many('fgmed.canvas.aulas.conteudos', string='Conteúdos da Disciplina')
    fgmed_canvas_aulas_ids = fields.Many2many('fgmed.canvas.aulas', string='Aulas relacionadas')
    
    
class FgmedCanvasAulasConteudos(models.Model):
    _name = "fgmed.canvas.aulas.conteudos"
    _description = 'Contém os conteúdos das aulas das disciplinas disponíveis'

    tipo = fields.Selection([('video-base', 'Vídeo base'),('conteudo-obrigatorio', 'Conteúdo Obrigatório'),('material-complementar', 'Material complementar')], string="Tipo de Aula", required=True)
    fgmed_canvas_aulas_ids = fields.Many2many('fgmed.canvas.aulas', string='Aulas relacionadas')
    disciplina_ids = fields.Many2many('fgmed.canvas.modules', string='Disciplinas relacionadas')

class FgmedCanvasAulas(models.Model):
    _name = "fgmed.canvas.aulas"
    _description = 'Contém as aulas disponíveis'

    name = fields.Char(string='Nome')
    fgmed_disciplina_id = fields.Many2many('fgmed.canvas.modules', string='Disciplinas relacionadas')
    fgmed_canvas_aulas_conteudos_ids = fields.Many2many('fgmed.canvas.aulas.conteudos', string='Conteúdos das aulas relacionadas')