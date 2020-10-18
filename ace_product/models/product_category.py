# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    ##############
    # New Fields #
    ##############

    is_mandrel = fields.Boolean(string='Mandrel Category', help='Check this box if this is a specific category for mandrels')

    # Product custom fields visibility
    show_family_code = fields.Boolean(string='Show Family Code', default=True)
    show_technical_description = fields.Boolean(string='Show Technical Description', default=True)
    show_formula_code = fields.Boolean(string='Show Formula Code', default=True)
    show_color_code = fields.Boolean(string='Show Color Code', default=True)
    show_commercial_name = fields.Boolean(string='Show Commercial Name', default=True)
    show_packing_norm = fields.Boolean(string='Show Packing Norm', default=True)
    show_pallet_type = fields.Boolean(string='Show Pallet Type', default=True)
    show_mandrel = fields.Boolean(string='Show Mandrel', default=True)

    show_is_sublot_jj = fields.Boolean(string='Show Sublot JJ', default=True)
    show_is_package_stored = fields.Boolean(string='Show Storage by Package', default=True)
    show_is_surface_treatment = fields.Boolean(string='Show Surface Treatment', default=True)

    show_coil_position = fields.Boolean(string='Show Coil Position', default=True)
    show_embossing_pattern = fields.Boolean(string='Show Embossing Pattern', default=True)
    show_substrate_position = fields.Boolean(string='Show Substrate Position', default=True)

    show_perforation_grid = fields.Boolean(string='Show Perforation Grid', default=True)

    show_coil_by_pallet = fields.Boolean(string='Show Coil by Pallet', default=True)
    show_coil_by_layer = fields.Boolean(string='Show Coil by Layer', default=True)
    show_layer_number = fields.Boolean(string='Show Number of Layers', default=True)

    show_thickness = fields.Boolean(string='Show Thickness', default=True)
    show_grammage = fields.Boolean(string='Show Grammage', default=True)
    show_ace_film_grammage = fields.Boolean(string='Show Ace Film Grammage', default=True)
    show_length = fields.Boolean(string='Show Length', default=True)
    show_width = fields.Boolean(string='Show Width', default=True)
    show_surface = fields.Boolean(string='Show Surface', default=True)
    show_diameter = fields.Boolean(string='Show Diameter', default=True)
    show_net_coil_weight = fields.Boolean(string='Show Net Coil Weight', default=True)
    show_gross_coil_weight = fields.Boolean(string='Show Gross Coil Weight', default=True)
    show_density = fields.Boolean(string='Show Density', default=True)
    show_mandrel_diameter = fields.Boolean(string='Show Mandrel Diameter', default=True)
    show_mandrel_width = fields.Boolean(string='Show Mandrel Width', default=True)
    show_glue_grammage = fields.Boolean(string='Show Glue Grammage', default=True)
