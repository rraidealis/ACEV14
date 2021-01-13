# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class UoM(models.Model):
    _inherit = 'uom.uom'

    uom_template_id = fields.Many2one('uom.uom.template', string='UoM Template', help='Template used for creation of current UoM')
    related_uom_id = fields.Many2one('uom.uom', string='Related UoM', related='uom_template_id.related_uom_id', help='This related UOM is used as basis for conversion betweens uoms.')

