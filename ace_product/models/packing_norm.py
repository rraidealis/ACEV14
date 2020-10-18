# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PackingNorm(models.Model):
    _name = 'product.packing.norm'
    _order = 'name'

    name = fields.Char(string='Packing Norm')
