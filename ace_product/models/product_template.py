# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Default values

    def _default_meters_uom_id(self):
        uom = self.env.ref('uom.product_uom_meter', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.uom_categ_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    def _default_units_uom_id(self):
        uom = self.env.ref('uom.product_uom_unit', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.product_uom_categ_unit')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    def _default_kilograms_uom_id(self):
        uom = self.env.ref('uom.product_uom_kgm', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.product_uom_categ_kgm')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    def _default_cms_uom_id(self):
        uom = self.env.ref('uom.product_uom_cm', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.uom_categ_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'smaller')], limit=1)
        return uom

    def _default_millimeters_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_millimeter', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.uom_categ_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('factor', '=', '1000')], limit=1)
        return uom

    def _default_micrometers_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_micrometer', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.uom_categ_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('factor', '=', '1000000')], limit=1)
        return uom

    def _default_square_meters_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_square_meter', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_data.product_uom_categ_surface')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    def _default_grammage_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_grammage', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_data.product_uom_categ_grammage')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    def _default_density_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_density', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_data.product_uom_categ_density')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    ##############
    # New Fields #
    ##############

    # O2m fields
    current_bom_line_ids = fields.One2many('mrp.bom.line', 'parent_product_tmpl_id', string='BoM Lines', help='Utility field')

    # M2o fields
    family_code_id = fields.Many2one('product.family.code', string='Family Code')
    technical_description_id = fields.Many2one('product.technical.description', string='Technical Description')
    formula_code_id = fields.Many2one('product.formula.code', string='Formula Code')
    color_code_id = fields.Many2one('product.color.code', string='Color Code')
    commercial_name_id = fields.Many2one('product.commercial.name', string='Commercial Name')
    packing_norm_id = fields.Many2one('product.packing.norm', string='Packing Norm')
    pallet_type_id = fields.Many2one('product.pallet.type', string='Pallet Type')
    embossing_pattern_id = fields.Many2one('product.embossing.pattern', string='Embossing Pattern')
    substrate_position_id = fields.Many2one('product.substrate.position', string='Substrate Position')
    mandrel_id = fields.Many2one('product.product', compute='_compute_mandrel_id', store=True, string='Mandrel', help='Provided by BoM lines if there is at least one BoM line with a mandrel product')
    perforation_grid_id = fields.Many2one('product.perforation.grid', string='Perforation Grid')
    surface_treatment_id = fields.Many2one('product.surface.treatment', string='Surface Treatment')

    # Boolean fields
    is_sublot_jj = fields.Boolean(string='Sublot JJ')
    is_package_stored = fields.Boolean(string='Storage by Package')

    # Selection fields
    coil_position = fields.Selection([('vertical', 'Vertical'), ('horizontal', 'Horizontal')], string='Coil Position')

    # Integer fields with units
    coil_by_pallet = fields.Integer(string='Coil by Pallet', compute='_compute_coil_by_pallet', store=True)
    coil_by_pallet_uom_id = fields.Many2one('uom.uom', string='Coil by Pallet UoM', readonly=True, default=_default_units_uom_id)
    coil_by_pallet_uom_name = fields.Char(string='Coil by Pallet UoM Label', related='coil_by_pallet_uom_id.name')

    coil_by_layer = fields.Integer(string='Coil by Layer')
    coil_by_layer_uom_id = fields.Many2one('uom.uom', string='Coil by Layer UoM', readonly=True, default=_default_units_uom_id)
    coil_by_layer_uom_name = fields.Char(string='Coil by Layer UoM Label', related='coil_by_layer_uom_id.name')

    layer_number = fields.Integer(string='Number of Layers')
    layer_number_uom_id = fields.Many2one('uom.uom', string='Number of Layers UoM', readonly=True, default=_default_units_uom_id)
    layer_number_uom_name = fields.Char(string='Number of Layers UoM Label', related='layer_number_uom_id.name')

    # Float fields with units
    thickness = fields.Float(string='Thickness', digits='Product Double Precision')
    thickness_uom_id = fields.Many2one('uom.uom', string='Thickness UoM', readonly=True, default=_default_micrometers_uom_id)
    thickness_uom_name = fields.Char(string='Thickness UoM Label', related='thickness_uom_id.name')

    extruded_film_grammage = fields.Float(string='Extruded Film Grammage', compute='_compute_extruded_film_grammage', store=True, digits='Product Single Precision')
    extruded_film_grammage_uom_id = fields.Many2one('uom.uom', string='Extruded Film Grammage UoM', readonly=True, default=_default_grammage_uom_id)
    extruded_film_grammage_uom_name = fields.Char(string='Extruded Film Grammage UoM Label', related='extruded_film_grammage_uom_id.name')
    manual_extruded_film_grammage = fields.Float(string='Manual Extruded Film Grammage', digits='Product Single Precision')
    is_extruded_film_grammage_user_defined = fields.Boolean(string='User Defined Extruded Film Grammage')

    total_grammage = fields.Float(string='Total Grammage', related='extruded_film_grammage', digits='Product Single Precision')
    total_grammage_uom_id = fields.Many2one('uom.uom', string='Total Grammage UoM', readonly=True, default=_default_grammage_uom_id)
    total_grammage_uom_name = fields.Char(string='Total Grammage UoM Label', related='total_grammage_uom_id.name')
    manual_total_grammage = fields.Float(string='Manual Total Grammage', digits='Product Single Precision')
    is_total_grammage_user_defined = fields.Boolean(string='User Defined Total Grammage')

    ace_film_grammage = fields.Float(string='Ace Film Grammage', related='extruded_film_grammage', digits='Product Single Precision')
    ace_film_grammage_uom_id = fields.Many2one('uom.uom', string='Ace Film Grammage UoM', readonly=True, default=_default_grammage_uom_id)
    ace_film_grammage_uom_name = fields.Char(string='Ace Film Grammage UoM Label', related='ace_film_grammage_uom_id.name')
    manual_ace_film_grammage = fields.Float(string='Manual Ace Film Grammage', digits='Product Single Precision')
    is_ace_film_grammage_user_defined = fields.Boolean(string='User Defined Ace Film Grammage')

    ace_length = fields.Float(string='Length', digits='Product Triple Precision')
    length_uom_id = fields.Many2one('uom.uom', string='Length UoM', readonly=True, default=_default_meters_uom_id)
    length_uom_name = fields.Char(string='Length UoM Label', related='length_uom_id.name')

    width = fields.Float(string='Width', digits='Product Single Precision')
    width_uom_id = fields.Many2one('uom.uom', string='Width UoM', readonly=True, default=_default_millimeters_uom_id)
    width_uom_name = fields.Char(string='Width UoM Label', related='width_uom_id.name')

    manual_weight = fields.Float(string='Manual Weight', digits='Product Triple Precision')
    is_weight_user_defined = fields.Boolean(string='User Defined Weight')

    surface = fields.Float(string='Surface', compute='_compute_surface', store=True, digits='Product Triple Precision')
    surface_uom_id = fields.Many2one('uom.uom', string='Surface UoM', readonly=True, default=_default_square_meters_uom_id)
    surface_uom_name = fields.Char(string='Surface Uom Label', related='surface_uom_id.name')

    diameter = fields.Float(string='Diameter', digits='Product Double Precision')
    diameter_uom_id = fields.Many2one('uom.uom', string='Diameter UoM', readonly=True, default=_default_millimeters_uom_id)
    diameter_uom_name = fields.Char(string='Diameter UoM Label', related='diameter_uom_id.name')

    net_coil_weight = fields.Float(string='Net Coil Weight', compute='_compute_coil_weight', store=True, digits='Product Triple Precision')
    net_coil_weight_uom_id = fields.Many2one('uom.uom', string='Net Coil Weight UoM', readonly=True, default=_default_kilograms_uom_id)
    net_coil_weight_uom_name = fields.Char(string='Net Coil Weight UoM Label', related='net_coil_weight_uom_id.name')

    gross_coil_weight = fields.Float(string='Gross Coil Weight', compute='_compute_coil_weight', store=True, digits='Product Triple Precision')
    gross_coil_weight_uom_id = fields.Many2one('uom.uom', string='Gross Coil Weight UoM', readonly=True, default=_default_kilograms_uom_id)
    gross_coil_weight_uom_name = fields.Char(string='Gross Coil Weight UoM Label', related='gross_coil_weight_uom_id.name')

    density = fields.Float(string='Density', compute='_compute_density', store=True)
    density_uom_id = fields.Many2one('uom.uom', string='Density UoM', readonly=True, default=_default_density_uom_id)
    density_uom_name = fields.Char(string='Density UoM Label', related='density_uom_id.name')

    mandrel_diameter = fields.Float(string='Mandrel Diameter', compute='_compute_mandrel_dimensions', store=True, digits='Product Double Precision')
    mandrel_diameter_uom_id = fields.Many2one('uom.uom', string='Mandrel Diameter UoM', readonly=True, default=_default_cms_uom_id)
    mandrel_diameter_uom_name = fields.Char(string='Mandrel Diameter UoM Label', related='mandrel_diameter_uom_id.name')

    mandrel_width = fields.Float(string='Mandrel Width', compute='_compute_mandrel_dimensions', store=True, digits='Product Double Precision')
    mandrel_width_uom_id = fields.Many2one('uom.uom', string='Mandrel Width UoM', readonly=True, default=_default_cms_uom_id)
    mandrel_width_uom_name = fields.Char(string='Mandrel Width UoM Label', related='mandrel_width_uom_id.name')

    mandrel_weight = fields.Float(string='Mandrel Weight', related='mandrel_id.weight', store=True, digits='Product Triple Precision')
    mandrel_weight_uom_id = fields.Many2one('uom.uom', string='Mandrel Weight UoM', readonly=True, default=_default_kilograms_uom_id)
    mandrel_weight_uom_name = fields.Char(string='Mandrel Weight UoM Label', related='mandrel_weight_uom_id.name')

    glue_grammage = fields.Float(string='Glue Grammage', digits='Product Double Precision')
    glue_grammage_uom_id = fields.Many2one('uom.uom', readonly=True, string='Glue Grammage UoM', default=_default_grammage_uom_id)
    glue_grammage_uom_name = fields.Char(string='Glue Grammage UoM Label', related='glue_grammage_uom_id.name')

    # Form visibility
    show_family_code = fields.Boolean(string='Show Family Code', related='categ_id.show_family_code')
    show_technical_description = fields.Boolean(string='Show Technical Description', related='categ_id.show_technical_description')
    show_formula_code = fields.Boolean(string='Show Formula Code', related='categ_id.show_formula_code')
    show_color_code = fields.Boolean(string='Show Color Code', related='categ_id.show_color_code')
    show_commercial_name = fields.Boolean(string='Show Commercial Name', related='categ_id.show_commercial_name')
    show_packing_norm = fields.Boolean(string='Show Packing Norm', related='categ_id.show_packing_norm')
    show_pallet_type = fields.Boolean(string='Show Pallet Type', related='categ_id.show_pallet_type')
    show_mandrel = fields.Boolean(string='Show Mandrel', related='categ_id.show_mandrel')
    show_is_sublot_jj = fields.Boolean(string='Show Sublot JJ', related='categ_id.show_is_sublot_jj')
    show_is_package_stored = fields.Boolean(string='Show Storage by Package', related='categ_id.show_is_package_stored')
    show_surface_treatment = fields.Boolean(string='Show Surface Treatment', related='categ_id.show_surface_treatment')
    show_coil_position = fields.Boolean(string='Show Coil Position', related='categ_id.show_coil_position')
    show_embossing_pattern = fields.Boolean(string='Show Embossing Pattern', related='categ_id.show_embossing_pattern')
    show_substrate_position = fields.Boolean(string='Show Substrate Position', related='categ_id.show_substrate_position')
    show_perforation_grid = fields.Boolean(string='Show Perforation Grid', related='categ_id.show_perforation_grid')
    show_coil_by_pallet = fields.Boolean(string='Show Coil by Pallet', related='categ_id.show_coil_by_pallet')
    show_coil_by_layer = fields.Boolean(string='Show Coil by Layer', related='categ_id.show_coil_by_layer')
    show_layer_number = fields.Boolean(string='Show Number of Layers', related='categ_id.show_layer_number')
    show_thickness = fields.Boolean(string='Show Thickness', related='categ_id.show_thickness')
    show_total_grammage = fields.Boolean(string='Show Total Grammage', related='categ_id.show_total_grammage')
    show_ace_film_grammage = fields.Boolean(string='Show Ace Film Grammage', related='categ_id.show_ace_film_grammage')
    show_extruded_film_grammage = fields.Boolean(string='Show Extruded Film Grammage', related='categ_id.show_extruded_film_grammage')
    show_width = fields.Boolean(string='Show Width', related='categ_id.show_width')
    show_length = fields.Boolean(string='Show Length', related='categ_id.show_length')
    show_surface = fields.Boolean(string='Show Surface', related='categ_id.show_surface')
    show_diameter = fields.Boolean(string='Show Diameter', related='categ_id.show_diameter')
    show_net_coil_weight = fields.Boolean(string='Show Net Coil Weight', related='categ_id.show_net_coil_weight')
    show_gross_coil_weight = fields.Boolean(string='Show Gross Coil Weight', related='categ_id.show_gross_coil_weight')
    show_density = fields.Boolean(string='Show Density', related='categ_id.show_density')
    show_mandrel_diameter = fields.Boolean(string='Show Mandrel Diameter', related='categ_id.show_mandrel_diameter')
    show_mandrel_width = fields.Boolean(string='Show Mandrel Width', related='categ_id.show_mandrel_width')
    show_mandrel_weight = fields.Boolean(string='Show Mandrel Weight', related='categ_id.show_mandrel_weight')
    show_glue_grammage = fields.Boolean(string='Show Glue Grammage', related='categ_id.show_glue_grammage')

    # SO visibility
    thickness_so_visibility = fields.Boolean(help='Thickness visibility in sale orders')
    total_grammage_so_visibility = fields.Boolean(help='Total Grammage visibility in sale orders')
    ace_film_grammage_so_visibility = fields.Boolean(help='Ace Film grammage visibility in sale orders')
    extruded_film_grammage_so_visibility = fields.Boolean(help='Extruded Film grammage visibility in sale orders')
    length_so_visibility = fields.Boolean(help='Length visibility in sale orders')
    width_so_visibility = fields.Boolean(help='Width visibility in sale orders')
    surface_so_visibility = fields.Boolean(help='Surface visibility in sale orders')
    diameter_so_visibility = fields.Boolean(help='Diameter visibility in sale orders')
    net_coil_weight_so_visibility = fields.Boolean(help='Net coil weight visibility in sale orders')
    gross_coil_weight_so_visibility = fields.Boolean(help='Gross coil weight visibility in sale orders')
    density_so_visibility = fields.Boolean(help='Density visibility in sale orders')
    family_code_so_visibility = fields.Boolean(help='Family code visibility in sale orders')
    technical_description_so_visibility = fields.Boolean(help='Technical description visibility in sale orders')
    formula_code_so_visibility = fields.Boolean(help='Formula code visibility in sale orders')
    color_code_so_visibility = fields.Boolean(help='Color code visibility in sale orders')
    commercial_name_so_visibility = fields.Boolean(help='Commercial name visibility in sale orders')

    ####################
    # Computed Methods #
    ####################

    @api.depends('thickness', 'density', 'manual_extruded_film_grammage', 'is_extruded_film_grammage_user_defined')
    def _compute_extruded_film_grammage(self):
        for product in self:
            product.extruded_film_grammage = 0.0
            if product.is_extruded_film_grammage_user_defined:
                product.extruded_film_grammage = product.manual_extruded_film_grammage
            elif product.thickness and product.density:
                product.extruded_film_grammage = product.thickness * product.density

    @api.depends('color_code_id', 'formula_code_id')
    def _compute_density(self):
        for product in self:
            product.density = 0.0
            if product.color_code_id and product.formula_code_id:
                theoretical_density = self.env['product.theoretical.density'].search([('color_code_id', '=', product.color_code_id.id),
                                                                                      ('formula_code_id', '=', product.formula_code_id.id)], limit=1)
                product.density = theoretical_density.density_uom_id._compute_quantity(theoretical_density.density, product.density_uom_id)

    @api.depends('current_bom_line_ids.product_id',
                 'current_bom_line_ids.product_id.categ_id',
                 'current_bom_line_ids.product_id.categ_id.is_mandrel')
    def _compute_mandrel_id(self):
        for product in self:
            product.mandrel_id = False
            bom_lines = product.current_bom_line_ids.filtered(lambda line: line.product_id.categ_id.is_mandrel)
            if bom_lines:
                product.mandrel_id = bom_lines[0].product_id

    @api.depends('width', 'ace_length')
    def _compute_surface(self):
        for product in self:
            width_factor = product.width_uom_id.factor
            length_factor = product.length_uom_id.factor
            product.surface = (product.width / width_factor) * (product.ace_length / length_factor)

    @api.depends('coil_by_layer', 'layer_number')
    def _compute_coil_by_pallet(self):
        for product in self:
            product.coil_by_pallet = product.coil_by_layer * product.layer_number

    @api.depends('surface', 'manual_ace_film_grammage', 'ace_film_grammage', 'is_ace_film_grammage_user_defined', 'mandrel_id', 'mandrel_id.weight')
    def _compute_coil_weight(self):
        for product in self:
            # Todo: Arbitrary divisor value, grams factor. Find a way to have a dynamic value since we didn't know that it is a conversion of g to kg
            weight = (product.surface * product.ace_film_grammage) / 1000
            if product.is_ace_film_grammage_user_defined:
                weight = (product.surface * product.manual_ace_film_grammage) / 1000
            product.net_coil_weight = weight
            if product.mandrel_id:
                weight_factor = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter().factor or 1
                weight += (product.mandrel_id.weight / weight_factor)
            product.gross_coil_weight = weight

    @api.depends('mandrel_id', 'mandrel_id.width', 'mandrel_id.diameter')
    def _compute_mandrel_dimensions(self):
        for product in self:
            product.mandrel_width = 0.0
            product.mandrel_diameter = 0.0
            if product.mandrel_id:
                width_factor = product.mandrel_id.width_uom_id.factor
                mandrel_width_factor = product.mandrel_width_uom_id.factor
                diameter_factor = product.mandrel_id.diameter_uom_id.factor
                mandrel_diameter_factor = product.mandrel_diameter_uom_id.factor
                product.mandrel_width = (product.mandrel_id.width / width_factor) * mandrel_width_factor
                product.mandrel_diameter = (product.mandrel_id.diameter / diameter_factor) * mandrel_diameter_factor

    @api.depends('product_variant_ids', 'product_variant_ids.weight', 'gross_coil_weight', 'manual_weight', 'is_weight_user_defined')
    def _compute_weight(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            if template.is_weight_user_defined:
                template.weight = template.manual_weight
            elif template.gross_coil_weight > 0:
                weight_factor = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter().factor or 1
                gross_coil_weight_factor = template.gross_coil_weight_uom_id.factor
                template.weight = (template.gross_coil_weight / gross_coil_weight_factor) * weight_factor
            else:
                template.weight = template.product_variant_ids.weight
        for template in (self - unique_variants):
            if template.is_weight_user_defined:
                template.weight = template.manual_weight
            else:
                template.weight = 0.0
