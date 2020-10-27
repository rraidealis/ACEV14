# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CarrotType(models.Model):
    _name = 'bom.carrot.type'
    _order = 'name'

    name = fields.Char(string='Carrot Type', required=True)
