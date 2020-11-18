# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from decimal import Decimal
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def _default_millimeters_uom_id(self):
        uom = self.env.ref('ace_product.product_uom_millimeter', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_product.product_uom_categ_small_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    def _default_micrometers_uom_id(self):
        uom = self.env.ref('ace_product.product_uom_micrometer', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_product.product_uom_categ_small_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'smaller')], limit=1)
        return uom

    def _default_density_uom_id(self):
        uom = self.env.ref('ace_product.product_uom_density', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_product.product_uom_categ_density')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    # Changes to existing fields
    product_qty = fields.Float(required=False)  # handle in view
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=False)  # handle in view
    type = fields.Selection(selection_add=[('recipe', 'Recipe')], ondelete={'recipe': 'set default'})

    # utility fields
    is_recipe = fields.Boolean(string='Is Recipe', store=True, compute='_compute_is_recipe', help='Field used to display recipe fields')

    # Char fields
    recipe_number = fields.Char('Number', readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('mrp.bom'))

    # O2m fields
    extruder_ids = fields.One2many('mrp.bom.extruder', 'bom_id', string='Extruders')

    # M2o fields
    formula_code_id = fields.Many2one('product.formula.code', string='Formula Code')
    color_code_id = fields.Many2one('product.color.code', string='Color Code')
    workcenter_id = fields.Many2one('mrp.routing.workcenter', string='Work Center')

    # Float fields with units
    min_thickness = fields.Float(string='Min Thickness', digits='Product Double Precision')
    max_thickness = fields.Float(string='Max Thickness', digits='Product Double Precision')
    thickness_uom_id = fields.Many2one('uom.uom', string='Thickness UoM', readonly=True, default=_default_micrometers_uom_id)
    thickness_uom_name = fields.Char(string='Thickness UoM Label', related='thickness_uom_id.name')

    min_width = fields.Float(string='Min Width', digits='Product Single Precision')
    max_width = fields.Float(string='Max Width', digits='Product Single Precision')
    width_uom_id = fields.Many2one('uom.uom', string='Width UoM', readonly=True, default=_default_millimeters_uom_id)
    width_uom_name = fields.Char(string='Width UoM Label', related='width_uom_id.name')

    density = fields.Float(string='Density')
    density_uom_id = fields.Many2one('uom.uom', string='Density UoM', readonly=True, default=_default_density_uom_id)
    density_uom_name = fields.Char(string='Density UoM Label', related='density_uom_id.name')

    @api.constrains('extruder_ids')
    def _check_extruders_concentration(self):
        for bom in self:
            if bom.is_recipe and bom.extruder_ids:
                precision = self.env['decimal.precision'].precision_get('BoM Concentration Precision')
                total = float_round(sum(bom.extruder_ids.mapped('concentration')), precision_digits=precision)
                if float_compare(total, 100.0, precision_digits=precision) != 0:
                    raise ValidationError(_('Total concentration of BoM\'s extruders is {}% (should be 100%).').format(total))

    @api.constrains('bom_line_ids')
    def _check_bom_lines_concentration(self):
        for bom in self:
            if bom.is_recipe and bom.bom_line_ids:
                precision = self.env['decimal.precision'].precision_get('BoM Concentration Precision')
                total = float_round(sum(bom.bom_line_ids.mapped('concentration')), precision_digits=precision)
                if float_compare(total, 100.0, precision_digits=precision) != 0:
                    raise ValidationError(_('Total concentration of BoM lines is {}% (should be 100%).').format(total))
                for line in bom.bom_line_ids:
                    if float_compare(line.layer_total_concentration, 100.0, precision_digits=precision) != 0:
                        raise ValidationError(_('All layers should have a total concentration of 100% (total concentration of layer {} is {}%).')
                                              .format(line.extruder_id.display_name, line.layer_total_concentration))

    @api.depends('type')
    def _compute_is_recipe(self):
        for bom in self:
            bom.is_recipe = True if bom.type == 'recipe' else False

    def action_view_production_boms(self):
        """ Action used on button box to open production boms related to current recipe bom """
        action = self.env.ref('mrp.mrp_bom_form_action')
        result = action.read()[0]
        result['domain'] = "[('type', '=', 'normal')]"
        return result

