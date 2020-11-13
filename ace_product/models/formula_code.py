# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class FormulaCode(models.Model):
    _name = 'product.formula.code'
    _description = 'Product Formula Code'
    _order = 'code'
    _record_name = 'code'

    code = fields.Char(string='Formula Code', required=True)

    def name_get(self):
        res = []
        for formula_code in self:
            name = formula_code.code
            res.append((formula_code.id, name))
        return res
