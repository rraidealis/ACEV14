# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EmbossingPattern(models.Model):
    _name = 'product.embossing.pattern'
    _order = 'name'

    name = fields.Char(string='Embossing Pattern')
