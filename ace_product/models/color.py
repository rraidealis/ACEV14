# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Color(models.Model):
    _name = 'product.color'
    _order = 'name'

    name = fields.Char(string='Color Name', required=True)
