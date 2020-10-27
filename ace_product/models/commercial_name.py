# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CommercialName(models.Model):
    _name = 'product.commercial.name'
    _order = 'name'

    name = fields.Char(string='Commercial Name', required=True)
