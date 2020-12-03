# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class UoMCategory(models.Model):
    _inherit = 'uom.category'

    category_template_id = fields.Many2one('uom.category.template', string='UoM Category Template', help='Template used for creation of current UoM category')
