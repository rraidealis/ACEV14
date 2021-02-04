# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    ##############
    # New Fields #
    ##############

    is_mandrel = fields.Boolean(string='Mandrel Category', help='Check this box if this is a specific category for mandrels')
    is_raw_mat = fields.Boolean(string='Raw Material Category', help='Check this box if this is a specific category for raw materials')
    is_subcontracted_film = fields.Boolean(string='Subcontracted Film Category', help='Check this box if this is a specific category for subcontracted films')
    is_film = fields.Boolean(string='Film Category', compute='_compute_is_film', store=True, help='Used in UI')
    is_ace_film = fields.Boolean(string='Ace Film Category', help='Check this box if this is a specific category for ACE films')
    is_coating = fields.Boolean(string='Coating Category', help='Check this box if this is a specific category for coatings')
    is_glue = fields.Boolean(string='Glue Category', help='Check this box if this is a specific category for glues')
    is_waste = fields.Boolean(string='Waste Category', help='Check this box if this is a specific category for waste coming from production')
    is_packaging = fields.Boolean(string='Packaging Category', help='Check this box if this is a specific category for packaging products')
    film_type = fields.Selection([('none', 'None'), ('laminated', 'Laminated'), ('glued', 'Glued'), ('extruded', 'Extruded')], default='none', string='Film Type')

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
    show_surface_treatment = fields.Boolean(string='Show Surface Treatment', default=True)

    show_coil_position = fields.Boolean(string='Show Coil Position', default=True)
    show_embossing_pattern = fields.Boolean(string='Show Embossing Pattern', default=True)
    show_substrate_position = fields.Boolean(string='Show Substrate Position', default=True)

    show_perforation_grid = fields.Boolean(string='Show Perforation Grid', default=True)

    show_coil_by_pallet = fields.Boolean(string='Show Coil by Pallet', default=True)
    show_coil_by_layer = fields.Boolean(string='Show Coil by Layer', default=True)
    show_layer_number = fields.Boolean(string='Show Number of Layers', default=True)
    show_coil_by_package = fields.Boolean(string='Show Coil by Package', default=True)
    show_stretch_program = fields.Boolean(string='Show Stretch Program', default=True)

    show_thickness = fields.Boolean(string='Show Thickness', default=True)
    show_total_grammage = fields.Boolean(string='Show Total Grammage', default=True)
    show_ace_film_grammage = fields.Boolean(string='Show Ace Film Grammage', default=True)
    show_extruded_film_grammage = fields.Boolean(string='Show Extruded Film Grammage', default=True)
    show_length = fields.Boolean(string='Show Length', default=True)
    show_width = fields.Boolean(string='Show Width', default=True)
    show_surface = fields.Boolean(string='Show Surface', default=True)
    show_diameter = fields.Boolean(string='Show Diameter', default=True)
    show_net_coil_weight = fields.Boolean(string='Show Net Coil Weight', default=True)
    show_gross_coil_weight = fields.Boolean(string='Show Gross Coil Weight', default=True)
    show_density = fields.Boolean(string='Show Density', default=True)
    show_mandrel_diameter = fields.Boolean(string='Show Mandrel Diameter', default=True)
    show_mandrel_width = fields.Boolean(string='Show Mandrel Width', default=True)
    show_mandrel_weight = fields.Boolean(string='Show Mandrel Weight', default=True)
    show_glue_grammage = fields.Boolean(string='Show Glue Grammage', default=True)

    @api.depends('is_subcontracted_film', 'is_ace_film')
    def _compute_is_film(self):
        for categ in self:
            categ.is_film = categ.is_subcontracted_film or categ.is_ace_film

    @api.onchange('is_ace_film')
    def _onchange_film_type(self):
        if not self.is_ace_film:
            self.film_type = 'none'

    def action_show_fields(self):
        self.ensure_one()
        show_all = self.env.context.get('show_category_fields')
        self.write({'show_stretch_program': show_all, 'show_family_code': show_all, 'show_technical_description': show_all, 'show_formula_code': show_all,
                    'show_color_code': show_all, 'show_commercial_name': show_all, 'show_packing_norm': show_all,
                    'show_pallet_type': show_all, 'show_mandrel': show_all, 'show_is_sublot_jj': show_all, 'show_is_package_stored': show_all,
                    'show_surface_treatment': show_all, 'show_coil_position': show_all, 'show_embossing_pattern': show_all,
                    'show_substrate_position': show_all, 'show_perforation_grid': show_all, 'show_coil_by_pallet': show_all,
                    'show_coil_by_layer': show_all, 'show_layer_number': show_all, 'show_thickness': show_all,
                    'show_total_grammage': show_all, 'show_ace_film_grammage': show_all, 'show_extruded_film_grammage': show_all,
                    'show_length': show_all, 'show_width': show_all, 'show_surface': show_all, 'show_diameter': show_all,
                    'show_net_coil_weight': show_all, 'show_gross_coil_weight': show_all, 'show_density': show_all,
                    'show_mandrel_diameter': show_all, 'show_mandrel_width': show_all, 'show_mandrel_weight': show_all, 'show_glue_grammage': show_all})


