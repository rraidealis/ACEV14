# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ColorCode(models.Model):
    _name = 'product.color.code'
    _order = 'code'
    _record_name = 'code'

    code = fields.Char(string='Color Code', required=True)
    color_id = fields.Many2one('product.color', string='Color', required=True)

    def name_get(self):
        res = []
        for color_code in self:
            name = '{}-{}'.format(color_code.code, color_code.color_id.name)
            res.append((color_code.id, name))
        return res
