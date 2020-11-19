# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class ImportRecipe(models.TransientModel):
    _name = 'mrp.bom.import.recipe'
    _description = 'Import BoM Recipe in order to fill components'

    def _default_kilograms_uom_id(self):
        uom = self.env.ref('uom.product_uom_kgm', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.product_uom_categ_kgm')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    bom_id = fields.Many2one('mrp.bom', string='Production BoM', required=True, domain=[('type', '=', 'standard')])
    recipe_bom_id = fields.Many2one('mrp.bom', string='Recipe BoM', domain=[('type', '=', 'recipe')])
    recipe_weight = fields.Float(string='Recipe Raw Weight', digits='Product triple Precision', help='Weight of raw materials used in recipe')
    recipe_weight_uom_id = fields.Many2one('uom.uom', string='Weight UoM', default=_default_kilograms_uom_id)
    uom_category_id = fields.Many2one('uom.category', string='UoM Category', default=lambda self: self.env.ref('uom.product_uom_categ_kgm'), help='Default UoM category used for raw mat weight')

    def button_import_recipe(self):
        self.ensure_one()
        self.bom_id.bom_line_ids.filtered(lambda l: l.recipe_bom_line_id).unlink()
        if not self.recipe_bom_id:
            vals = {'workcenter_id': False, 'recipe_bom_id': False, 'recipe_weight': 0.0}
        else:
            for line in self.recipe_bom_id.bom_line_ids:
                bom_weight = self.recipe_weight
                bom_weight_uom = self.recipe_weight_uom_id
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
                    'product_qty': bom_weight * (concentration / 100),
                    'recipe_bom_line_id': line.id})
            vals = {
                'workcenter_id': self.recipe_bom_id.workcenter_id.id or False,
                'recipe_bom_id': self.recipe_bom_id.id,
                'recipe_weight': self.recipe_weight or 0.0,
                'recipe_weight_uom_id': self.recipe_weight_uom_id.id}
        return self.bom_id.write(vals)

