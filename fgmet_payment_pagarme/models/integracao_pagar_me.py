# -*- coding: utf-8 -*-
from odoo import models, http, fields, api, exceptions, _
from odoo.http import request

from dateutil.relativedelta import relativedelta
# from datetime import timedelta
from datetime import datetime
import pytz
import uuid

class testPayment(models.Model):
    _inherit = "payment.transaction"
    @api.model
    def just_a_payment_test(self, data):
        self._set_transaction_done()
