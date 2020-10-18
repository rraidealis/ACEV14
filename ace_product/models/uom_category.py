# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class UoMCategory(models.Model):
    _inherit = 'uom.category'

    measure_type = fields.Selection(selection_add=[('small_length', 'Default Small Length'), ('grammage', 'Default Grammage'), ('surface', 'Default Surface'), ('density', 'Default Density'), ('speed', 'Default Speed')])
