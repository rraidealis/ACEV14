# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, _
from odoo.exceptions import UserError


class AddWasteManagement(models.TransientModel):
    _name = 'mrp.bom.add.waste.management'
    _description = 'Add Waste Management to BoM of a Glued, Laminated or Extruded Film'

    def _default_allowed_waste_category_ids(self):
        return [(6, 0, self.env['product.category'].search([('is_waste', '=', True)]).ids)]

    def _default_allowed_waste_uom_ids(self):
        categ = self.env.ref('uom.product_uom_categ_kgm')
        return [(6, 0, self.env['uom.uom'].search([('category_id', '=', categ.id)]).ids)]

    bom_id = fields.Many2one('mrp.bom', string='Production BoM', required=True)
    byproduct_id = fields.Many2one('product.product', string='By-Product', required=True, help='Product that registers waste during production')
    allowed_waste_category_ids = fields.Many2many('product.category', 'wiz_allowed_waste_categories_rel', 'wiz_id', 'category_id', string='Waste Categories', default=_default_allowed_waste_category_ids)
    allowed_waste_uom_ids = fields.Many2many('uom.uom', 'wiz_allowed_waste_uoms_rel', 'wiz_id', 'category_id', string='Waste UoMs', default=_default_allowed_waste_uom_ids)
    waste_qty_in_kg = fields.Float(string='Waste Quantity', related='bom_id.waste_qty_in_kg')
    border_waste_qty_in_kg = fields.Float(string='Border Waste Quantity', related='bom_id.border_waste_qty_in_kg')

    def button_add_byproduct(self):
        self.ensure_one()
        # delete byproduct used to register waste
        self.bom_id.byproduct_id.unlink()
        # enable computation of waste quantities
        self.bom_id.waste_management_enabled = True
        # add byproduct
        if self.byproduct_id:
            kg_uom = self.env.ref('uom.product_uom_kgm')
            try:
                byproduct = self.env['mrp.bom.byproduct'].create({
                                                'bom_id': self.bom_id.id,
                                                'waste_management': True,
                                                'product_qty': kg_uom._compute_quantity(self.bom_id.waste_qty_in_kg, self.byproduct_id.uom_id),
                                                'product_id': self.byproduct_id.id,
                                                'product_uom_id': self.byproduct_id.uom_id.id})
                self.bom_id.byproduct_id = byproduct
            except Exception:
                raise UserError(_('It is not possible to input waste on by-product {} (maybe this product does not handle kilograms).').format(self.byproduct_id.name))
        # recompute components quantity
        for film in self.bom_id.bom_line_ids.filtered(lambda line: line.is_film_component):
            film.product_qty = self.recompute_film_qty(film)
        for component in self.bom_id.bom_line_ids.filtered(lambda line: line.is_glue_component or line.is_coating_component):
            component.product_qty = self.recompute_component_qty(component)

    def recompute_film_qty(self, film):
        # 1a. Retrieving quantity to produce in meters
        # retrieve uom related to meters
        meters_uom = self.env.ref('uom.product_uom_meter')
        custom_uom_related_to_meters = self.env['uom.uom'].search([('category_id', '=', self.bom_id.product_uom_id.category_id.id), ('related_uom_id', '=', meters_uom.id)], limit=1)
        # convert quantity to produce in this uom
        if custom_uom_related_to_meters:
            qty_to_produce_in_meters = self.bom_id.product_uom_id._compute_quantity(self.bom_id.product_qty, custom_uom_related_to_meters)
        else:
            qty_to_produce_in_meters = 0.0

        # 1b. Retrieving waste quantity to produce in meters
        # retrieve uom related to kilograms
        kg_uom = self.env.ref('uom.product_uom_kgm')
        custom_uom_related_to_kgs = self.env['uom.uom'].search([('category_id', '=', self.bom_id.product_uom_id.category_id.id), ('related_uom_id', '=', kg_uom.id)], limit=1)
        # convert quantity to produce from kilograms to meters
        if custom_uom_related_to_kgs:
            qty_to_produce_in_meters += custom_uom_related_to_kgs._compute_quantity(self.bom_id.waste_qty_in_kg, custom_uom_related_to_meters)

        # 2. Applying stretching factor if any
        if film.stretching_factor:
            stretched_qty_to_produce_in_meters = qty_to_produce_in_meters - (qty_to_produce_in_meters * film.stretching_factor)
        else:
            stretched_qty_to_produce_in_meters = qty_to_produce_in_meters

        # 3. Converting stretched quantity in the same uom as the component one
        # retrieve an UoM linked to a length UoM and in the same category than the component UoM category
        custom_uom_related_to_meters = self.env['uom.uom'].search([('category_id', '=', film.product_id.uom_id.category_id.id), ('related_uom_id', '=', meters_uom.id)], limit=1)
        if custom_uom_related_to_meters:
            return custom_uom_related_to_meters._compute_quantity(stretched_qty_to_produce_in_meters, film.product_uom_id)
        else:
            return 0.0

    def recompute_component_qty(self, component):
        if component.grammage and component.film_component_to_treat and component.coverage_factor:
            # 1. get component quantity in square meters
            surface_uom = self.env.ref('ace_data.product_uom_square_meter')
            custom_uom_related_to_surface_uom = self.env['uom.uom'].search([('category_id', '=', component.film_component_to_treat.product_uom_id.category_id.id),
                                                                           ('related_uom_id', '=', surface_uom.id)], limit=1)
            component_qty_in_square_meters = component.film_component_to_treat.product_uom_id._compute_quantity(component.film_component_to_treat.product_qty, custom_uom_related_to_surface_uom)
            # 2. compute glue quantity in kg (need component surface)
            glue_qty_in_kg = (component.grammage * component_qty_in_square_meters * component.coverage_factor) / 1000
            # 3. convert qty in component uom
            kg_uom = self.env.ref('uom.product_uom_kgm')
            return kg_uom._compute_quantity(glue_qty_in_kg, component.product_uom_id)
        else:
            return 0.0
