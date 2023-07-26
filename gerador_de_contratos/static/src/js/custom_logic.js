odoo.define('gerador_de_contratos.custom_logic', function (require) {
    "use strict";

    // Importando os módulos necessários
    var FormController = require('web.FormController');
    var fieldRegistry = require('web.field_registry');
    var basicFields = require('web.basic_fields');

    // Criando um novo campo de seleção personalizado para as variáveis
    var VariableSelection = basicFields.FieldSelection.extend({
        events: _.extend({}, basicFields.FieldSelection.prototype.events, {
            'change': '_onVariableSelectionChange',  // Adicionando um novo manipulador de eventos
        }),
        
        init: function() {
            this._super.apply(this, arguments);

            this.values = [
                ['amount_total', 'Total'],
                ['payment_term_id', 'Termo de pagamento'],
                // Adicione mais variáveis aqui conforme necessário
            ];
        },

        // Quando a seleção muda, a variável é adicionada ao final do campo de conteúdo
        _onVariableSelectionChange: function() {
            var variableName = this.$el.val();  // Obtendo a variável selecionada
            var contentField = this.getParent().getField('content');  // Obtendo o campo de conteúdo
            
            if (contentField && contentField.$input) {
                var variableTag = '{{' + variableName + '}}';  // Formatando a variável
                contentField.$input.val(contentField.$input.val() + variableTag);  // Adicionando a variável ao campo de conteúdo  // Adicionando a variável ao campo de conteúdo
            }
        },
    });

    // Registrando o novo widget no registro de campos
    fieldRegistry.add('variable_selection', VariableSelection);

    // Personalizando o controlador do formulário
    var CustomFormController = FormController.extend({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.modelName === 'gerador_views') {
                this.$buttons.find('.o_form_button_save').css("display", "none");
                this.$buttons.find('.o_form_button_cancel').css("display", "none");
                $('body').addClass('gerador-de-contratos');
            } else {
                $('body').removeClass('gerador-de-contratos');
            }
        },
    });

    // Exportando os novos widgets
    return {
        CustomFormController: CustomFormController,
        VariableSelection: VariableSelection,
    };
});
