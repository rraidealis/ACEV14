# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PalletType(models.Model):
    _name = 'product.pallet.type'
    _order = 'name'

    name = fields.Char(string='Pallet Type', required=True)
