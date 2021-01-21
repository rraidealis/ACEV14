# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    startup_time = fields.Float(string='Startup Time', help='Time in minutes before production be fully effective')
    waste_percentage = fields.Float(string='Waste Percentage', digits='Percentage Quadruple Precision', help='Percentage of wasted quantity according quantity to produce')
