# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SurfaceTreatment(models.Model):
    _name = 'product.surface.treatment'
    _description = 'Product Surface Treatment'
    _order = 'name'

    name = fields.Char(string='Surface Treatment', required=True)
