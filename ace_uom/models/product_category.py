# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    uom_category_template_id = fields.Many2one('uom.category.template', string='UoM Category Template', help='Used to generate new UoMs for product of this category')
