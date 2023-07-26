odoo.define("meu_modulo.my_js", function (require) {
  "use strict";

  var core = require("web.core");
  var WebClient = require("web.WebClient");

  WebClient.include({
    start: function () {
      var self = this;
      return this._super.apply(this, arguments).then(function () {
        var color = core.config.theme_my_modulo.color || "#ffffff";
        var css = core.qweb.render("MeuModulo.FooterCss", { color: color });
        self.$el.find("#my-footer").after(css);
      });
    },
  });
});
