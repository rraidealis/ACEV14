# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class FamilyCode(models.Model):
    _name = 'product.family.code'
    _description = 'Product Family Code'
    _order = 'code'
    _record_name = 'code'

    code = fields.Char(string='Family Code', required=True)

    def name_get(self):
        res = []
        for family_code in self:
            # TODO : pourquoi passer par la variable intermédiaire name? res.append((family_code.id, family_code.code)) suffirait
            name = family_code.code
            res.append((family_code.id, name))
        return res
