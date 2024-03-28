from odoo import models, fields, api

class CourseManagementWizard(models.TransientModel):
    _name = 'course.creation.wizard'
    _description = 'Gerenciamento de Menus'
    
# Menus

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
        
    def action_menu_curriculos(self):
        view_id3 = self.env.ref('modelo_de_cursos_e_matricula.view_curriculo_creation_form').id
        return {
            'name': 'Base de Currículos',
            'type': 'ir.actions.act_window',
            'res_model': 'course.creation.wizard',
            'view_mode': 'form',
            'view_id': view_id3,
            'target': 'new',
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'}
        }

    def action_menu_ingresso_suspensao(self):
        view_id4 = self.env.ref('modelo_de_cursos_e_matricula.view_tipo_creation_form').id
        return {
            'name': 'Base de Ingressos e Suspensões',
            'type': 'ir.actions.act_window',
            'res_model': 'course.creation.wizard',
            'view_mode': 'form',
            'view_id': view_id4,
            'target': 'new',
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'}
        }
        
    def action_open_matricula_creation_form(self):
        view_id = self.env.ref('modelo_de_cursos_e_matricula.view_matricula_creation_form').id
        return {
            'name': 'Criar Matrícula',
            'type': 'ir.actions.act_window',
            'res_model': 'course.creation.wizard',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'}
        }        

# Botoões de criação        

    def action_criar_discipline(self):
        return {
            'name': 'Criar Disciplina',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.disciplina',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_criar_tipo_ingresso(self):
        return {
            'name': 'Criar Tipo ingresso',
            'type': 'ir.actions.act_window',
            'res_model': 'tipo.de.ingresso',
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_criar_curriculo(self):
        return {
            'name': 'Criar Currículo',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.curriculo',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_criar_versao_curriculo(self):
        return {
            'name': 'Criar Versão de Currículo',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.curriculo.variant',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_criar_curso(self):
        return {
            'name': 'Criar Curso',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.cursos',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_criar_matricula(self):
        return {
            'name': 'Criar Matrícula',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.matricula',
            'view_mode': 'form',
            'target': 'new',
        }


# Botoões de vizualização        

    def action_ver_discipline(self):
        return {
            'name': 'Ver Disciplina',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.disciplina',
            'view_mode': 'tree',
            'target': 'new',
        }

    def action_ver_tipo_ingresso(self):
        return {
            'name': 'Ver Tipo ingresso',
            'type': 'ir.actions.act_window',
            'res_model': 'tipo.de.ingresso',
            'view_mode': 'tree',
            'target': 'new',
        }
    
    def action_ver_curriculo(self):
        return {
            'name': 'Ver Currículo',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.curriculo',
            'view_mode': 'tree',
            'target': 'new',
        }

    def action_ver_versao_curriculo(self):
        return {
            'name': 'Ver Versão de Currículo',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.curriculo.variant',
            'view_mode': 'tree',
            'target': 'new',
        }

    def action_ver_curso(self):
        return {
            'name': 'Ver Curso',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.cursos',
            'view_mode': 'tree',
            'target': 'new',
        }

    def action_ver_matricula(self):
        return {
            'name': 'Ver Matrícula',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.matricula',
            'view_mode': 'kanban',
            'target': 'new',
        }

    def action_ver_quadro(self):
        view_id5 = self.env.ref('modelo_de_cursos_e_matricula.view_matricula_kanban').id
        return {
            'name': 'Quadro de Alunos',
            'type': 'ir.actions.act_window',
            'res_model': 'informa.matricula',
            'context':{'group_by': 'curso', 'default_from_specific_menu': True},
            'view_mode':'kanban',
            'view_id': view_id5,
            'target': 'new',
        }