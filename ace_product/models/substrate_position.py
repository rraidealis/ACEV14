# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SubstratePosition(models.Model):
    _name = 'product.substrate.position'
    _order = 'position'
    _record_name = 'position'

    position = fields.Char(string='Substrate Position')

    def name_get(self):
        res = []
        for substrate_pos in self:
            name = substrate_pos.position
            res.append((substrate_pos.id, name))
        return res
