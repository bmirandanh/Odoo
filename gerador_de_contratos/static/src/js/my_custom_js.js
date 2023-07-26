odoo.define('gerador_de_contratos.FormController', function(require) {
    "use strict";

    var FormController = require('web.FormController');

    FormController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.modelName === 'gerador_views') {
                this.$buttons.find('.o_form_button_save').hide();
                this.$buttons.find('.o_form_button_cancel').hide();
                this.$buttons.find('.o_dropdown_toggler_btn btn btn-secondary').hide();
                this.$buttons.find('.o_pager_counter').hide();
                this.$buttons.find('.fa fa-chevron-left btn btn-secondary o_pager_previous').hide();
                this.$buttons.find('.fa fa-chevron-right btn btn-secondary o_pager_next').hide();
            }
        },
    });
});