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
        self.bom_id.byproduct_id.unlink()
        if self.byproduct_id:
            kg_uom = self.env.ref('uom.product_uom_kgm')
            try:
                byproduct = self.env['mrp.bom.byproduct'].create({
                                                'bom_id': self.bom_id.id,
                                                'waste_management': True,
                                                'product_qty': kg_uom._compute_quantity(self.waste_qty_in_kg, self.byproduct_id.uom_id),
                                                'product_id': self.byproduct_id.id,
                                                'product_uom_id': self.byproduct_id.uom_id.id})
                self.bom_id.byproduct_id = byproduct
            except Exception:
                raise UserError(_('It is not possible to input waste on by-product {} (maybe this product does not handle kilograms).').format(self.byproduct_id.name))
