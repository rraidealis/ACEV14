# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MrpBomExtruder(models.Model):
    _name = 'mrp.bom.extruder'
    _description = 'BoM Extruder'
    _order = 'name'

    bom_id = fields.Many2one('mrp.bom', string='Parent BoM', ondelete='cascade', required=True)
    name = fields.Char(string='Name', required=True)
    concentration = fields.Float(string='Concentration', digits='BoM Concentration Precision', required=True)

    def name_get(self):
        res = []
        for extruder in self:
            name = '{}({}%)'.format(extruder.name, extruder.concentration)
            res.append((extruder.id, name))
        return res
