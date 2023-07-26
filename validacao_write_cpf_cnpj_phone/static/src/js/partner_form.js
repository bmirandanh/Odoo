odoo.define('seu_modulo.partner_form', function (require) {
    'use strict';

    var FormController = require('web.FormController');
    var FormRenderer = require('web.FormRenderer');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');
    var fieldRegistry = require('web.field_registry');
    var FieldChar = require('web.basic_fields').FieldChar;

    FormRenderer.include({
        _renderTagInput: function (node) {
            var result = this._super.apply(this, arguments);
            if (node.attrs.name === 'l10n_br_cnpj_cpf_formatted') {
                var self = this;
                this.state.dataReady.done(function() {
                    var l10n_br_cnpj_cpf_placeholder = self.state.data.l10n_br_cnpj_cpf_placeholder;
                    if (l10n_br_cnpj_cpf_placeholder) {
                        result.attrs.placeholder = l10n_br_cnpj_cpf_placeholder;
                        self.$("input[name='l10n_br_cnpj_cpf_formatted']").attr('placeholder', l10n_br_cnpj_cpf_placeholder);
                    }
                });
            }
            return result;
        },
    });

    var PartnerCNPJCPFField = FieldChar.extend({
        events: _.extend({}, FieldChar.prototype.events, {
            'change': '_onChange',
        }),

        _renderReadonly: function () {
            this._super.apply(this, arguments);
            var formattedValue = formatCNPJCPF(this.value);
            this.$el.text(formattedValue);
        },

        _renderEdit: function () {
            this._super.apply(this, arguments);
            var formattedValue = formatCNPJCPF(this.value);
            this.$input.val(formattedValue);
        },

        _onChange: function (event) {
            this._super.apply(this, arguments);
            var formattedValue = this.$input.val();
            var unformattedValue = formattedValue.replace(/[^\d]/g, '');
            this.trigger_up('field_changed', {
                dataPointID: this.dataPointID,
                changes: { l10n_br_cnpj_cpf: unformattedValue },
            });
        },
    });

    fieldRegistry.add('cnpjcpf', PartnerCNPJCPFField);

    var PartnerFormController = FormController.extend({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
            field_changed: '_onFieldChanged',
        }),

        _onFieldChanged: function (ev) {
            this._super.apply(this, arguments);
            if (ev.data.changes && (ev.data.changes.l10n_br_legal_name || ev.data.changes.l10n_br_legal_name === false)) {
                var l10n_br_legal_name_visible = this.renderer.$el.find("input[name='l10n_br_legal_name']").is(':visible');
                var l10n_br_cnpj_cpf_placeholder = l10n_br_legal_name_visible ? 'CPF' : 'CNPJ';
                this.renderer.$el.find("input[name='l10n_br_cnpj_cpf_formatted']").attr('placeholder', l10n_br_cnpj_cpf_placeholder);
            }
        },
    });

    var PartnerFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Renderer: FormRenderer,
            Controller: PartnerFormController,
        }),
    });

    viewRegistry.add('partner_form', PartnerFormView);

    return {
        PartnerCNPJCPFField: PartnerCNPJCPFField,
        PartnerFormView: PartnerFormView,
    };
});
