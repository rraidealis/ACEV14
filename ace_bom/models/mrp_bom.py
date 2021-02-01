# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_round

LIMIT_OF_FILM_COMPONENTS = 2

class MrpBom(models.Model):
    _name = 'mrp.bom'
    _inherit = ['mrp.bom', 'mail.activity.mixin']

    def _default_millimeters_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_millimeter', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_data.product_uom_categ_small_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    def _default_micrometers_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_micrometer', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_data.product_uom_categ_small_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'smaller')], limit=1)
        return uom

    def _default_density_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_density', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_data.product_uom_categ_density')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    def _default_kilograms_uom_id(self):
        uom = self.env.ref('uom.product_uom_kgm', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.product_uom_categ_kgm')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    #####################
    # Changes to fields #
    #####################
    # -> recipe requirements
    product_tmpl_id = fields.Many2one('product.template', required=False)  # handle in view
    product_qty = fields.Float(required=False, digits='Product Triple Precision')  # handle in view
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=False)  # handle in view
    type = fields.Selection(selection_add=[('recipe', 'Recipe')], ondelete={'recipe': 'set default'})
    ##################
    # Utility fields #
    ##################
    # -> recipe requirement
    is_recipe = fields.Boolean(string='Is Recipe', compute='_compute_is_recipe', help='Field used to display recipe fields')
    # -> general requirement
    film_type_bom = fields.Selection(string='Film Type', related='product_tmpl_id.categ_id.film_type', help='Field used to display information relative to film type')
    # -> waste management
    waste_management_enabled = fields.Boolean(string='Waste Management', help='Field used to active waste management')
    #########
    # Chars #
    #########
    # -> recipe requirement
    recipe_number = fields.Char(string='Number', readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('mrp.bom'))
    ############
    # Integers #
    ############
    # -> recipe requirement
    production_bom_count = fields.Integer(string='Production BoMs Count', compute='_compute_production_bom_count')
    ##############
    # O2m fields #
    ##############
    # -> recipe requirements
    extruder_ids = fields.One2many('mrp.bom.extruder', 'bom_id', string='Extruders')
    production_bom_ids = fields.One2many('mrp.bom', 'recipe_bom_id', string='Production BoMs', readonly=True, domain=[('type', '=', 'normal')])  # only recipes have production BoMs
    alt_bom_line_ids = fields.One2many('mrp.bom.line', 'alt_bom_id', string='Alternative BoM Lines', help='Alternative recipe lines')  # it is not possible to use bom_line_ids field for alternative components
    ##############
    # M2o fields #
    ##############
    # -> recipe requirements
    recipe_bom_id = fields.Many2one('mrp.bom', string='Recipe', readonly=True, domain=[('type', '=', 'recipe')])
    formula_code_id = fields.Many2one('product.formula.code', string='Formula Code')
    color_code_id = fields.Many2one('product.color.code', string='Color Code')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center')
    # -> general requirement
    byproduct_id = fields.Many2one('mrp.bom.byproduct', string='Waste Product Management')
    ##########
    # Floats #
    ##########
    # -> recipe requirements
    min_thickness = fields.Float(string='Min Thickness', digits='Product Double Precision')
    max_thickness = fields.Float(string='Max Thickness', digits='Product Double Precision')
    thickness_uom_id = fields.Many2one('uom.uom', string='Thickness UoM', readonly=True, default=_default_micrometers_uom_id)
    thickness_uom_name = fields.Char(string='Thickness UoM Label', related='thickness_uom_id.name')

    min_width = fields.Float(string='Min Width', digits='Product Single Precision')
    max_width = fields.Float(string='Max Width', digits='Product Single Precision')
    width_uom_id = fields.Many2one('uom.uom', string='Width UoM', readonly=True, default=_default_millimeters_uom_id)
    width_uom_name = fields.Char(string='Width UoM Label', related='width_uom_id.name')

    density = fields.Float(string='Density', compute='_compute_density', store=True)
    density_uom_id = fields.Many2one('uom.uom', string='Density UoM', readonly=True, default=_default_density_uom_id)
    density_uom_name = fields.Char(string='Density UoM Label', related='density_uom_id.name')

    raw_mat_weight = fields.Float(string='Raw Mat Weight', digits='Product Triple Precision', compute='_compute_raw_mat_weight', store=True, tracking=True, help='Weight of raw materials used to produce this product')
    raw_mat_weight_uom_id = fields.Many2one('uom.uom', string='Weight UoM', readonly=True, default=_default_kilograms_uom_id)
    raw_mat_weight_uom_name = fields.Char(string='Weight UoM Label', related='raw_mat_weight_uom_id.name')

    waste_uom_id = fields.Many2one('uom.uom', string='Waste UoM', readonly=True, default=_default_kilograms_uom_id)
    waste_uom_name = fields.Char(string='Weight Waste Label', related='waste_uom_id.name')
    border_waste_qty_in_kg = fields.Float(string='Border Waste Quantity', digits='Product Triple Precision', compute='_compute_waste_qty_in_kg', store=True, tracking=True, help='Quantity of waste based on borders of ACE film components')
    waste_qty_in_kg = fields.Float(string='Waste Quantity', digits='Product Triple Precision', compute='_compute_waste_qty_in_kg', store=True, tracking=True, help='Quantity of waste based on startup parameters, waste factors on BoM and workcenter, and film components borders.\n'
                                                                                                                 'Formula:\n'
                                                                                                                 'A) machine speed in m/minutes * startup time in minutes * (production width in millimeters % 1000) * (film grammage in g/m² % 1000)\n'
                                                                                                                 'B) (result A / (production width in millimeters % 1000)) * (product width in millimeters % 1000) * number of times product is present\n'
                                                                                                                 'C) result B + quantity to produce in meters * (BoM waste percentage + workcenter waste percentage)\n'
                                                                                                                 'D) result C + (components quantity in meters - result C) * border factor\n'
                                                                                                                 'E) convert result D in kilograms')

    @api.constrains('extruder_ids')
    def _check_extruders_concentration(self):
        """ Check if total concentration of extruders is 100% """
        precision = self.env['decimal.precision'].precision_get('BoM Concentration Precision')
        for bom in self:
            if bom.is_recipe and bom.extruder_ids:
                total = float_round(sum(bom.extruder_ids.mapped('concentration')), precision_digits=precision)
                if float_compare(total, 1.0, precision_digits=precision) != 0:
                    raise ValidationError(_('Total concentration of BoM\'s extruders is {}% (should be 100%).').format(total * 100))

    @api.constrains('bom_line_ids')
    def _check_bom_lines_film_limit(self):
        """ Check if total of film components does not exceed limit """
        for bom in self:
            if bom.film_type_bom == 'glued' and len(bom.bom_line_ids.filtered(lambda l: l.product_id.categ_id.is_film)) > LIMIT_OF_FILM_COMPONENTS:
                raise ValidationError(_('You reached limit of film components for this bill of materials (max: {}, found: {}).')
                                      .format(LIMIT_OF_FILM_COMPONENTS, len(bom.bom_line_ids.filtered(lambda l: l.product_id.categ_id.is_film))))

    @api.constrains('bom_line_ids')
    def _check_bom_lines_concentration(self):
        """ Check concentration of components of a recipe and components of a production BoM linked to a recipe """
        precision = self.env['decimal.precision'].precision_get('BoM Concentration Precision')
        for bom in self:
            # check production BoM lines concentration
            if bom.type == 'normal' and bom.recipe_bom_id:
                total = float_round(sum(bom.bom_line_ids.mapped('related_concentration')), precision_digits=precision)
                if float_compare(total, 1.0, precision_digits=precision) != 0:
                    raise ValidationError(_('Total concentration of recipe components is {}% (should be 100%).').format(total * 100))
            # check recipe BoM lines concentration
            elif bom.is_recipe and bom.bom_line_ids:
                total = float_round(sum(bom.bom_line_ids.mapped('concentration')), precision_digits=precision)
                if float_compare(total, 1.0, precision_digits=precision) != 0:
                    raise ValidationError(_('Total concentration of recipe components is {}% (should be 100%).').format(total * 100))
                # since it is possible to set a concentration above 100% on a line in order to have a total of 100%,
                # we should check if all layers have a total concentration of 100%
                for line in bom.bom_line_ids:
                    if float_compare(line.layer_total_concentration, 1.0, precision_digits=precision) != 0:
                        raise ValidationError(_('All layers should have a total concentration of 100% (total concentration of layer {} is {}%).')
                                              .format(line.extruder_id.display_name, line.layer_total_concentration * 100))

    @api.constrains('alt_bom_line_ids')
    def _check_alt_bom_lines_concentration(self):
        """ Check concentration of alternative components of a recipe """
        precision = self.env['decimal.precision'].precision_get('BoM Concentration Precision')
        for bom in self:
            if bom.is_recipe and bom.alt_bom_line_ids:
                total = float_round(sum(bom.alt_bom_line_ids.mapped('concentration')), precision_digits=precision)
                if float_compare(total, 1.0, precision_digits=precision) != 0:
                    raise ValidationError(_('Total concentration of alternative BoM lines is {}% (should be 100%).').format(total * 100))
                for line in bom.alt_bom_line_ids:
                    if float_compare(line.layer_total_concentration, 1.0, precision_digits=precision) != 0:
                        raise ValidationError(_('All layers should have a total concentration of 100% (total concentration of layer {} is {}%).')
                                              .format(line.extruder_id.display_name, line.layer_total_concentration * 100))

    @api.depends('product_tmpl_id',
                 'product_tmpl_id.extruded_film_grammage',
                 'product_qty',
                 'product_uom_id',
                 'recipe_bom_id',
                 'waste_qty_in_kg')
    def _compute_raw_mat_weight(self):
        for bom in self:
            if bom.film_type_bom in ['extruded', 'laminated']:
                # retrieve quantity to produce in kg
                kg_uom = self.env.ref('uom.product_uom_kgm')
                custom_uom_related_to_kgs = self.env['uom.uom'].search([('category_id', '=', bom.product_uom_id.category_id.id), ('related_uom_id', '=', kg_uom.id)], limit=1)
                qty_to_produce_in_kgs = bom.product_uom_id._compute_quantity(bom.product_qty, custom_uom_related_to_kgs) if custom_uom_related_to_kgs else 0.0
                qty_to_produce_in_kgs += bom.waste_qty_in_kg
                # retrieve quantity to produce in units
                units_uom = self.env.ref('uom.product_uom_unit')
                custom_uom_related_to_units = self.env['uom.uom'].search([('category_id', '=', bom.product_uom_id.category_id.id), ('related_uom_id', '=', units_uom.id)], limit=1)
                qty_to_produce_in_units = custom_uom_related_to_kgs._compute_quantity(qty_to_produce_in_kgs, custom_uom_related_to_units) if custom_uom_related_to_kgs and custom_uom_related_to_units else 0.0

                # multiply raw mat by quantity to produce in units
                weight = (bom.product_tmpl_id.surface * bom.product_tmpl_id.extruded_film_grammage) / 1000
                bom.raw_mat_weight = weight * qty_to_produce_in_units

                if bom.recipe_bom_id:
                    # compute product quantity for each line bound to recipe
                    for line in bom.bom_line_ids.filtered(lambda l: l.recipe_bom_line_id):
                        bom_weight = bom.raw_mat_weight
                        bom_weight_uom = bom.raw_mat_weight_uom_id
                        line_uom = line.product_uom_id
                        concentration = line.related_concentration
                        # convert uoms between line product and raw weight
                        if bom_weight_uom.category_id == line_uom.category_id:
                            bom_weight = bom_weight_uom._compute_quantity(bom_weight, line_uom)
                        else:
                            raise UserError(_(
                                'Cannot convert UoMs while importing recipe. UoMs categories should be the same on the BoM ({}) and the component ({}).').format(
                                bom_weight_uom.display_name, line_uom.display_name))
                        line.product_qty = bom_weight * concentration
            else:
                bom.raw_mat_weight = 0.0

    @api.depends('waste_management_enabled',
                 'product_tmpl_id.total_grammage',
                 'product_qty',
                 'product_uom_id',
                 'recipe_bom_id',
                 'product_tmpl_id.width',
                 'workcenter_id.waste_percentage',
                 'machine_speed',
                 'workcenter_id.startup_time',
                 'machine_time_number',
                 'waste_percentage',
                 'total_production_width',
                 'bom_line_ids.product_qty')
    def _compute_waste_qty_in_kg(self):
        for bom in self:
            if bom.waste_management_enabled and bom.film_type_bom in ['extruded', 'laminated', 'glued']:
                # retrieve quantity to produce in kg
                kg_uom = self.env.ref('uom.product_uom_kgm')
                custom_uom_related_to_kgs = self.env['uom.uom'].search([('category_id', '=', bom.product_uom_id.category_id.id), ('related_uom_id', '=', kg_uom.id)], limit=1)
                qty_to_produce_in_kgs = bom.product_uom_id._compute_quantity(bom.product_qty, custom_uom_related_to_kgs) if custom_uom_related_to_kgs else 0.0
                waste_qty_in_kgs = 0.0
                # compute workcenter and bom waste quantity
                if bom.workcenter_id and bom.workcenter_id.waste_percentage:
                    waste_qty_in_kgs += qty_to_produce_in_kgs * (bom.workcenter_id.waste_percentage + bom.waste_percentage)
                else:
                    waste_qty_in_kgs += qty_to_produce_in_kgs * bom.waste_percentage
                # compute startup waste quantity
                if bom.machine_speed and bom.workcenter_id and bom.workcenter_id.startup_time and bom.machine_time_number and bom.total_production_width:
                    # for full production width
                    # m/minutes * minutes * mm * g/m²
                    startup_waste_qty_in_kgs = bom.machine_speed * bom.workcenter_id.startup_time * (bom.total_production_width / 1000) * (bom.product_tmpl_id.total_grammage / 1000)
                    # for current product / production width
                    # (kg / mm) * mm * number
                    waste_qty_in_kgs += (startup_waste_qty_in_kgs / (bom.total_production_width / 1000)) * (bom.product_tmpl_id.width / 1000) * bom.machine_time_number
                bom.waste_qty_in_kg = waste_qty_in_kgs
                # compute border waste quantity
                border_waste_qty_in_kg = 0.0
                for component in bom.bom_line_ids.filtered(lambda line: line.is_film_component):
                    meters_uom = self.env.ref('uom.product_uom_meter')
                    custom_uom_related_to_meters = self.env['uom.uom'].search([('category_id', '=', bom.product_uom_id.category_id.id), ('related_uom_id', '=', meters_uom.id)], limit=1)
                    qty_to_produce_in_meters = bom.product_uom_id._compute_quantity(bom.product_qty, custom_uom_related_to_meters)
                    stretched_qty_to_produce_in_meters = qty_to_produce_in_meters - (qty_to_produce_in_meters * component.stretching_factor)
                    wasted_surface = stretched_qty_to_produce_in_meters * ((component.product_id.width / 1000) * component.border_factor)
                    border_waste_qty_in_kg += wasted_surface * (component.grammage / 1000)
                bom.border_waste_qty_in_kg = border_waste_qty_in_kg
                if bom.byproduct_id:
                    # update by-product quantity to register waste quantity
                    try:
                        bom.byproduct_id.write({'product_qty': waste_qty_in_kgs + border_waste_qty_in_kg, 'product_uom_id': kg_uom.id})
                    except Exception:
                        raise UserError(_('It is not possible to input waste on by-product {} (maybe this product does not handle kilograms).').format(bom.byproduct_id.name))
            else:
                bom.waste_qty_in_kg = 0.0
                bom.border_waste_qty_in_kg = 0.0

    @api.depends('type')
    def _compute_is_recipe(self):
        for bom in self:
            bom.is_recipe = True if bom.type == 'recipe' else False

    @api.depends('bom_line_ids.density', 'bom_line_ids.concentration', 'bom_line_ids.product_id.density')
    def _compute_density(self):
        """ Compute bom density according to lines density """
        precision = self.env['decimal.precision'].precision_get('Product Double Precision')
        for bom in self:
            recipe_bom_lines = bom.bom_line_ids.filtered(lambda line: line.density and line.concentration)
            bom.density = float_round(sum([line.density*line.concentration for line in recipe_bom_lines]), precision_digits=precision)

    @api.depends('production_bom_ids')
    def _compute_production_bom_count(self):
        """ Count production BoMs """
        for bom in self:
            bom.production_bom_count = len(bom.production_bom_ids)

    @api.onchange('type')
    def _onchange_bom_type(self):
        """ Clean product and quantity if BoM type is recipe """
        if self.type == 'recipe':
            self.product_tmpl_id = False
            self.product_id = False
            self.product_qty = 1.0

    def write(self, vals):
        res = super(MrpBom, self).write(vals)
        # TODO : do we still need to display an exception if recipe information change ?
        # if 'workcenter_id' in vals or 'type' in vals:
        #     for bom in self.production_bom_ids:
        #         bom.activity_schedule(
        #             act_type_xmlid='mail.mail_activity_data_warning',
        #             date_deadline=date.today(),
        #             summary=_('Recipe has changed'),
        #             note=_('Recipe ({}) has changed. To apply changes to current BoM, you should re-import the recipe.').format(self.display_name),
        #             user_id=self.env.uid)
        return res

    def name_get(self):
        """
        Overwritten method
        Use standard formatting if bom is not a recipe,
        else display name should use recipe number instead of product template display name
        """
        return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', bom.product_tmpl_id.display_name if not bom.is_recipe else bom.recipe_number)) for bom in self]

    def action_view_production_boms(self):
        """ Action used on button box to open production boms related to current recipe bom """
        self.ensure_one()
        action = self.env.ref('mrp.mrp_bom_form_action')
        result = action.read()[0]
        result['domain'] = [('id', 'in', self.production_bom_ids.ids)]
        return result

    def action_import_recipe_bom(self):
        """ Open a wizard in order to import a recipe """
        self.ensure_one()
        view = self.env.ref('ace_bom.mrp_bom_import_recipe_view_form')
        wiz = self.env['mrp.bom.import.recipe'].create({'bom_id': self.id})
        return {
            'name': _('Import Recipe'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mrp.bom.import.recipe',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }

    def action_add_component(self):
        """ Open a wizard in order to add film, glue and coating components """
        self.ensure_one()
        action = self.env.ref('ace_bom.bom_line_action_form_view')
        film_components_count = len(self.bom_line_ids.filtered(lambda l: l.product_id.categ_id.is_film))
        if self.env.context.get('default_allowed_category_type', '') == 'is_film':
            if film_components_count >= LIMIT_OF_FILM_COMPONENTS:
                raise UserError(_('You cannot add another film on this bill of materials (max: {}, found: {}). '
                                  'Please remove some film type components before considering adding a new one.').format(LIMIT_OF_FILM_COMPONENTS, film_components_count))
            action = self.env.ref('ace_bom.add_film_action_form_view')
        elif self.env.context.get('default_allowed_category_type', '') == 'is_glue':
            if film_components_count <= 1:
                raise UserError(_('You need at least two films to glue them together (found: {}).').format(film_components_count))
            action = self.env.ref('ace_bom.add_treatment_action_form_view')
        elif self.env.context.get('default_allowed_category_type', '') == 'is_coating':
            if film_components_count < 1:
                raise UserError(_('You need at least one film on which apply a coating.'))
            action = self.env.ref('ace_bom.add_treatment_action_form_view')
        return action.read()[0]

    def action_compute_recipe_quantities(self):
        """
        Compute recipe quantities if current bom is linked to a recipe
        Lines related to recipe components are deleted first, then a new line is added for each recipe component.
        """
        self.ensure_one()
        if self.recipe_bom_id:
            self.bom_line_ids.filtered(lambda l: l.recipe_bom_line_id).unlink()
            for line in self.recipe_bom_id.bom_line_ids:
                    bom_weight = self.raw_mat_weight
                    bom_weight_uom = self.raw_mat_weight_uom_id
                    line_uom = line.product_uom_id
                    concentration = line.concentration
                    # convert uoms between line product and raw weight
                    if bom_weight_uom.category_id == line_uom.category_id:
                        bom_weight = bom_weight_uom._compute_quantity(bom_weight, line_uom)
                    else:
                        raise UserError(_(
                            'Cannot convert UoMs while importing recipe. UoMs categories should be the same on the BoM ({}) and the component ({}).').format(
                            bom_weight_uom.display_name, line_uom.display_name))
                    self.env['mrp.bom.line'].create({
                        'bom_id': self.id,
                        'product_id': line.product_id.id,
                        'product_tmpl_id': line.product_id.product_tmpl_id.id,
                        'extruder_id': line.extruder_id.id or False,
                        'product_qty': bom_weight * concentration,
                        'recipe_bom_line_id': line.id})

    def unlink(self):
        """
        Overridden method
        Prevent user from deleting recipes. those should be archived instead.
        """
        recipes = self.filtered(lambda bom: bom.type == 'recipe')
        if recipes:
            msg = _('It is not possible to delete recipe ({}). Instead, you should archive it.')
            if len(recipes) > 1:
                msg = _('It is not possible to delete recipes ({}). Instead, you should archive them.')
            raise UserError(msg.format(' ,'.join(recipes.mapped('display_name'))))
        else:
            return super(MrpBom, self).unlink()
