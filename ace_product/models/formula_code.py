# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class FormulaCode(models.Model):
    _name = 'product.formula.code'
    _order = 'code'
    _record_name = 'code'

    code = fields.Char(string='Formula Code')
