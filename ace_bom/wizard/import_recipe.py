# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class ImportRecipe(models.TransientModel):
    _name = 'mrp.bom.import.recipe'
    _description = 'Import BoM Recipe in order to fill components'

    bom_id = fields.Many2one('mrp.bom', string='Production BoM', required=True, domain=[('type', '=', 'standard')])
    recipe_bom_id = fields.Many2one('mrp.bom', string='Recipe BoM', domain=[('type', '=', 'recipe')])

    def button_import_recipe(self):
        self.ensure_one()
        self.bom_id.bom_line_ids.filtered(lambda l: l.recipe_bom_line_id).unlink()
        if not self.recipe_bom_id:
            vals = {'workcenter_id': False, 'recipe_bom_id': False}
        else:
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
                    'product_qty': bom_weight * (concentration / 100),
                    'recipe_bom_line_id': line.id})
            vals = {
                'workcenter_id': self.recipe_bom_id.workcenter_id.id or False,
                'recipe_bom_id': self.recipe_bom_id.id}
        return self.bom_id.write(vals)

