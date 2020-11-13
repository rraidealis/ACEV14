# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PerforationGrid(models.Model):
    _name = 'product.perforation.grid'
    _description = 'Product Perforation Grid'
    _order = 'name'

    name = fields.Char(string='Perforation Grid', required=True)
