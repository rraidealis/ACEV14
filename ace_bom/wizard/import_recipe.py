# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ImportRecipe(models.TransientModel):
    _name = 'mrp.bom.import.recipe'
    _description = 'Import BoM Recipe in order to fill components'

    def _default_allowed_waste_category_ids(self):
        return [(6, 0, self.env['product.category'].search([('is_waste', '=', True)]).ids)]

    def _default_allowed_waste_uom_ids(self):
        categ = self.env.ref('uom.product_uom_categ_kgm')
        return [(6, 0, self.env['uom.uom'].search([('category_id', '=', categ.id)]).ids)]

    bom_id = fields.Many2one('mrp.bom', string='Production BoM', required=True, domain=[('type', '=', 'standard')])
    recipe_bom_id = fields.Many2one('mrp.bom', string='Recipe BoM', domain=[('type', '=', 'recipe')])
    by_product_id = fields.Many2one('product.product', string='By-Product', help='Product that registers waste during production')
    allowed_waste_category_ids = fields.Many2many('product.category', 'wiz_waste_categories_rel', 'wiz_id', 'category_id', string='Waste Categories', default=_default_allowed_waste_category_ids)
    allowed_waste_uom_ids = fields.Many2many('uom.uom', 'wiz_waste_uoms_rel', 'wiz_id', 'category_id', string='Waste UoMs', default=_default_allowed_waste_uom_ids)

    def button_import_recipe(self):
        self.ensure_one()
        self.bom_id.bom_line_ids.filtered(lambda l: l.recipe_bom_line_id).unlink()
        self.bom_id.byproduct_ids.filtered(lambda p: p.recipe_bom_id).unlink()
        vals = {}
        if not self.recipe_bom_id:
            vals.update({'workcenter_id': False, 'recipe_bom_id': False})
        else:
            if self.by_product_id:
                self.env['mrp.bom.byproduct'].create({
                    'bom_id': self.bom_id.id,
                    'product_qty': 0.0,
                    'product_id': self.by_product_id.id,
                    'product_uom_id': self.by_product_id.uom_id.id,
                    'recipe_bom_id': self.recipe_bom_id.id})
            bom_weight = self.bom_id.raw_mat_weight
            bom_weight_uom = self.bom_id.raw_mat_weight_uom_id
            for line in self.recipe_bom_id.bom_line_ids:
                line_uom = line.product_uom_id
                concentration = line.concentration
                if bom_weight_uom.category_id == line_uom.category_id:
                    bom_weight = bom_weight_uom._compute_quantity(bom_weight, line.product_uom_id)
                else:
                    raise UserError(_('Cannot convert UoMs while importing recipe. UoMs categories should be the same on the BoM ({}) and the component ({}).').format(bom_weight_uom.display_name, line_uom.display_name))
                self.env['mrp.bom.line'].create({
                    'bom_id': self.bom_id.id,
                    'product_id': line.product_id.id,
                    'product_tmpl_id': line.product_id.product_tmpl_id.id,
                    'extruder_id': line.extruder_id.id or False,
                    'product_qty': bom_weight * concentration,
                    'recipe_bom_line_id': line.id})
            vals.update({
                'workcenter_id': self.recipe_bom_id.workcenter_id.id or False,
                'recipe_bom_id': self.recipe_bom_id.id})
        return self.bom_id.write(vals)

