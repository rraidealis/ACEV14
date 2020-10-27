# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    # Default values

    def _default_units_uom_id(self):
        uom = self.env.ref('uom.product_uom_unit', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.product_uom_categ_unit')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    def _default_millimeters_uom_id(self):
        uom = self.env.ref('ace_product.product_uom_millimeter', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.uom_categ_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('factor', '=', '1000')], limit=1)
        return uom

    def _default_meters_per_minute_uom_id(self):
        uom = self.env.ref('ace_product.product_uom_meter_per_minute', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_product.product_uom_categ_speed')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'smaller')], limit=1)
        return uom

    ##############
    # New Fields #
    ##############

    # M2o fields
    carrot_type_id = fields.Many2one('bom.carrot.type', string='Carrot Type')

    # Integer fields with units
    machine_time_number = fields.Integer(string='Number of Times')
    machine_time_number_uom_id = fields.Many2one('uom.uom', string='Number of Times UoM', readonly=True, default=_default_units_uom_id)
    machine_time_number_uom_name = fields.Char(string='Number of Times UoM Label', readonly=True, related='machine_time_number_uom_id.name')

    # Float fields with units
    total_production_width = fields.Float(string='Total Production Width', digits='Product Single Precision')
    total_production_width_uom_id = fields.Many2one('uom.uom', string='Production Width UoM', readonly=True, default=_default_millimeters_uom_id)
    total_production_width_uom_name = fields.Char(string='Production Width UoM Label', readonly=True, related='total_production_width_uom_id.name')

    machine_speed = fields.Float(string='Standard Machine Speed', digits='Product Double Precision')
    machine_speed_uom_id = fields.Many2one('uom.uom', string='Machine Speed UoM', readonly=True, default=_default_meters_per_minute_uom_id)
    machine_speed_uom_name = fields.Char(string='Machine Speed UoM Label', readonly=True, related='machine_speed_uom_id.name')
