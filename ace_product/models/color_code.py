# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ColorCode(models.Model):
    _name = 'product.color.code'
    _order = 'code'
    _record_name = 'code'

    code = fields.Char(string='Family Code')

    def name_get(self):
        res = []
        for color_code in self:
            name = color_code.code
            res.append((color_code.id, name))
        return res
