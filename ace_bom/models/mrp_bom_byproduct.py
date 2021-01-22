# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MrpByProduct(models.Model):
    _inherit = 'mrp.bom.byproduct'

    waste_management = fields.Boolean(string='Waste Management', help='This byproduct records production waste')
