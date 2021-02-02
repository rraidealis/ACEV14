# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PackingNorm(models.Model):
    _name = 'product.packing.norm'
    _description = 'Product Packing Norm'
    _order = 'name'

    name = fields.Char(string='Packing Norm', required=True)
    packaging_bom_id = fields.Many2one('mrp.bom', string='Packaging Instructions', required=True, domain=[('type', '=', 'packaging')])

