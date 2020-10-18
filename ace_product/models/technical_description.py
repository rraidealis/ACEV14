# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class TechnicalDesc(models.Model):
    _name = 'product.technical.description'
    _order = 'desc'
    _record_name = 'desc'

    desc = fields.Char(string='Family Code')

    def name_get(self):
        res = []
        for tech_description in self:
            name = tech_description.desc
            res.append((tech_description.id, name))
        return res