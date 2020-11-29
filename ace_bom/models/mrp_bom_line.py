# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_round


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    def _default_density_uom_id(self):
        uom = self.env.ref('ace_product.product_uom_density', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_product.product_uom_categ_density')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    # changes to field
    bom_id = fields.Many2one('mrp.bom', required=False)  # field required handled in constrains

    # M2m fields
    allowed_uom_ids = fields.Many2many('uom.uom', string='Allowed UoMs', compute='_compute_allowed_uom_ids')

    # O2m fields
    production_bom_line_ids = fields.One2many('mrp.bom.line', 'recipe_bom_line_id', string='BoM Production Line', readonly=True)

    # M2o fields
    extruder_id = fields.Many2one('mrp.bom.extruder', string='Extruder', ondelete='cascade')
    recipe_bom_line_id = fields.Many2one('mrp.bom.line', string='BoM Recipe Line', readonly=True, ondelete='cascade') # if a production bom line is no longer linked to a recipe line, then it should be deleted
    alt_bom_id = fields.Many2one('mrp.bom', string='Parent Alternative BoM', ondelete='cascade', help='This is the BoM used for alternative components.')  # field required handled in constrains

    # Float fields with UoM
    density = fields.Float(string='Density', store=True, related='product_id.density', digits='Product Double Precision')
    density_uom_id = fields.Many2one('uom.uom', string='Density UoM', related='product_id.density_uom_id')
    density_uom_name = fields.Char(string='Density UoM Label', related='density_uom_id.name')

    # Concentration
    layer_concentration = fields.Float(string='Concentration per Layer', digits='BoM Concentration Precision')
    layer_total_concentration = fields.Float(string='Total Concentration per Layer', digits='BoM Concentration Precision', compute='_compute_layer_total_concentration')
    concentration = fields.Float(string='Concentration', digits='BoM Concentration Precision', store=True, compute='_compute_concentration')
    related_concentration = fields.Float(string='Recipe Concentration', digits='BoM Concentration Precision', related='recipe_bom_line_id.concentration', help='Concentration taken from recipe line')

    # Char fields
    hopper = fields.Char('Hopper')

    @api.constrains('bom_id', 'alt_bom_id')
    def _check_exist_bom(self):
        """
        Components and alternative components should be related to a BoM but it is not possible to use the same field.
        Thus, components are linked to bom_id and alternative components to alt_bom_id.
        In every cases those two are the same.
        """
        for line in self:
            if not line.bom_id and not line.alt_bom_id:
                raise ValidationError(_('BoM Line should be related to a BoM.'))

    def _compute_allowed_uom_ids(self):
        """ Components of a recipe should use UoMs from weight category """
        for line in self:
            if line.bom_id.type == 'recipe' or line.alt_bom_id.type == 'recipe':
                categ = self.env.ref('uom.product_uom_categ_kgm')
                uoms = self.env['uom.uom'].search([('category_id', '=', categ.id)])
            else:
                uoms = self.env['uom.uom'].search([])
            line.write({'allowed_uom_ids': [(6, 0, uoms.ids)]})

    @api.depends('layer_concentration', 'extruder_id', 'extruder_id.concentration')
    def _compute_concentration(self):
        """ Compute concentration of a component in the recipe """
        for line in self:
            line.concentration = 0.0
            if line.layer_concentration and line.extruder_id and line.extruder_id.concentration:
                line.concentration = line.layer_concentration * (line.extruder_id.concentration / 100)

    @api.depends('layer_concentration',
                 'extruder_id',
                 'bom_id.bom_line_ids',
                 'bom_id.bom_line_ids.extruder_id',
                 'bom_id.bom_line_ids.layer_concentration')
    def _compute_layer_total_concentration(self):
        """ Compute concentration of all components with the same extruder """
        for line in self:
            precision = self.env['decimal.precision'].precision_get('BoM Concentration Precision')
            if line.bom_id:
                line.layer_total_concentration = float_round(sum(line.bom_id.bom_line_ids.filtered(lambda l: l.extruder_id == line.extruder_id).mapped('layer_concentration')), precision_digits=precision)
            elif line.alt_bom_id:
                line.layer_total_concentration = float_round(sum(line.alt_bom_id.alt_bom_line_ids.filtered(lambda l: l.extruder_id == line.extruder_id).mapped('layer_concentration')), precision_digits=precision)
            else:
                line.layer_total_concentration = 0.0

    @api.model
    def create(self, values):
        """
        Overridden method
        If a new recipe component is created, a done exception is displayed on related production BoMs.
        Then compute again recipe components on those production BoMs.
        """
        res = super(MrpBomLine, self).create(values)
        recipe_lines = res.filtered(lambda l: l.bom_id and l.bom_id.production_bom_ids)
        for line in recipe_lines:
            for bom in line.bom_id.production_bom_ids:
                activity = bom.activity_schedule(
                    act_type_xmlid='mail.mail_activity_data_warning',
                    date_deadline=date.today(),
                    summary=_('Recipe has changed'),
                    note=_('Component ({}) has been added to recipe ({}). You should recompute quantities.').format(
                        line.product_id.name, line.bom_id.display_name),
                    user_id=self.env.uid)
                activity._action_done()
                bom.action_compute_recipe_quantities()
        return res

    def write(self, vals):
        """
        Overridden method

        If current line is from a recipe and not an alternative component from a recipe, and at least one information changed on the line
        (product, layer concentration or extruder), then a done exception should be displayed on production BoM.
        Those changes should be synchronized with production bom lines using this recipe.
        """
        res = super(MrpBomLine, self).write(vals)
        # if line has an alt_bom_id then line is an alternative components
        # and we don't need to synchronize or display an exception
        if not self.alt_bom_id and self.bom_id.type == 'recipe' and ('product_id' in vals or 'layer_concentration' in vals or 'extruder_id' in vals):
            # If parent BoM is a recipe, we display an exception on each production BoM using this recipe
            for bom in self.bom_id.production_bom_ids:
                activity = bom.activity_schedule(
                    act_type_xmlid='mail.mail_activity_data_warning',
                    date_deadline=date.today(),
                    summary=_('Recipe has changed'),
                    note=_('Component ({}) of recipe ({}) has changed. You should recompute quantities.').format(self.product_id.name, self.bom_id.display_name),
                    user_id=self.env.uid)
                # activity is automatically done since we synchronize lines
                activity._action_done()
                # synchronization: recompute recipe components on production BoM
                bom.action_compute_recipe_quantities()
        return res

    def unlink(self):
        """
        Overridden method
        If a recipe component is deleted then a done exception is displayed on related production BoMs
        and recipe components are computed again.
        """
        if self.alt_bom_id or self.bom_id.type != 'recipe':
            return super(MrpBomLine, self).unlink()
        else:
            recipe_bom = self.bom_id
            product = self.product_id
            res = super(MrpBomLine, self).unlink()
            for bom in recipe_bom.production_bom_ids:
                activity = bom.activity_schedule(
                    act_type_xmlid='mail.mail_activity_data_warning',
                    date_deadline=date.today(),
                    summary=_('Recipe has changed'),
                    note=_('Component ({}) of recipe ({}) has been deleted. You should recompute quantities.').format(product.name, recipe_bom.display_name),
                    user_id=self.env.uid)
                activity._action_done()
                bom.action_compute_recipe_quantities()
            return res