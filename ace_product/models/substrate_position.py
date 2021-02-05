# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SubstratePosition(models.Model):
    _name = 'product.substrate.position'
    _description = 'Product Substrate Position'
    _order = 'position'
    _record_name = 'position'

    position = fields.Char(string='Substrate Position', required=True)

    def name_get(self):
        res = []
        for substrate_pos in self:
            # TODO : passer par name?
            name = substrate_pos.position
            res.append((substrate_pos.id, name))
        return res
