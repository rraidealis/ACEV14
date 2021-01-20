# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class AddTreatment(models.TransientModel):
    _name = 'mrp.bom.add.treatment'
    _description = 'Add Coating/Glue product to BoM components of a Glued Film'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    def _default_grammage_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_grammage', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_data.product_uom_categ_grammage')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    is_coating_component = fields.Boolean(string='Is Coating Component', related='product_id.categ_id.is_coating')
    film_component_to_coat = fields.Many2one('mrp.bom.line', string='Film to Coat')  # domain handled in view
    film_component_to_treat = fields.Many2one('mrp.bom.line', store=True, compute='_compute_film_component_to_treat', string='Film to Treat')
    allowed_category_type = fields.Char(string='Product Category Type')
    allowed_product_category_ids = fields.Many2many('product.category', string='Allowed Categories', compute='_compute_allowed_product_category_ids')
    product_id = fields.Many2one('product.product', string='Component', required=True)
    product_qty = fields.Float(string='Quantity', compute='_compute_product_qty', digits='Product Unit of Measure')
    product_uom_id = fields.Many2one('uom.uom', string='Product Unit of Measure',
                                     help='Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control',
                                     domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_name = fields.Char(string='Product UoM Label', related='product_uom_id.name')
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    bom_id = fields.Many2one('mrp.bom', string='Production BoM', required=True)
    grammage = fields.Float(string='Grammage', default=1.0, digits='Product Single Precision')
    grammage_uom_id = fields.Many2one('uom.uom', string='Grammage UoM', readonly=True, default=_default_grammage_uom_id)
    grammage_uom_name = fields.Char(string='Grammage UoM Label', related='grammage_uom_id.name')
    coverage_factor = fields.Float(string='Coverage Factor', store=True, compute='_compute_coverage_factor', digits='Product Double Precision')

    @api.depends('allowed_category_type')
    def _compute_allowed_product_category_ids(self):
        for wiz in self:
            category_type = wiz.allowed_category_type
            categories = self.env['product.category'].search([('is_film', '=', False), ('is_glue', '=', False), ('is_coating', '=', False)])
            if category_type and category_type not in ['laminated', 'glued', 'extruded']:
                categories = categories.search([(category_type, '=', True)])
            elif category_type:
                categories = categories.search([('film_type', '=', category_type)])
            wiz.update({'allowed_product_category_ids': [(6, 0, categories.ids)]})

    @api.depends('product_id.categ_id', 'bom_id.bom_line_ids.coverage_factor', 'film_component_to_coat')
    def _compute_coverage_factor(self):
        """
        Compute coverage factor of component according to coverage factor of films.
        To glue films, use the film with the lowest coverage factor.
        To coat films, select a film to coat and use its coverage factor.
        """
        for wiz in self:
            wiz.coverage_factor = 0.0
            if wiz.product_id:
                if wiz.product_id.categ_id.is_glue:
                    film_coverage_factors = wiz.bom_id.bom_line_ids.filtered(lambda l: l.product_id.categ_id.is_film).mapped('coverage_factor')
                    wiz.coverage_factor = min(film_coverage_factors)
                elif wiz.product_id.categ_id.is_coating and wiz.film_component_to_coat:
                    wiz.coverage_factor = wiz.film_component_to_coat.coverage_factor

    @api.depends('film_component_to_coat', 'bom_id')
    def _compute_film_component_to_treat(self):
        """
        Film component to treat is the film component with the lowest coverage factor in case of glue.
        For coating, it is the film component selected by the user
        """
        for wiz in self:
            wiz.film_component_to_treat = False
            if wiz.film_component_to_coat:
                wiz.film_component_to_treat = wiz.film_component_to_coat
            elif wiz.bom_id.bom_line_ids.filtered(lambda l: l.product_id.categ_id.is_film and l.coverage_factor):
                films = wiz.bom_id.bom_line_ids.filtered(lambda l: l.product_id.categ_id.is_film and l.coverage_factor).sorted(key=lambda l: l.coverage_factor)
                if films:
                    wiz.film_component_to_treat = films[0] if len(films) > 1 else films

    @api.depends('grammage', 'film_component_to_treat', 'coverage_factor', 'bom_id', 'product_uom_id')
    def _compute_product_qty(self):
        for wiz in self:
            if wiz.grammage and wiz.film_component_to_treat and wiz.coverage_factor:
                # 1. get component quantity in square meters
                surface_uom = self.env.ref('ace_data.product_uom_square_meter')
                custom_uom_related_to_surface_uom = self.env['uom.uom'].search([('category_id', '=', wiz.film_component_to_treat.product_uom_id.category_id.id),
                                                                               ('related_uom_id', '=', surface_uom.id)], limit=1)
                component_qty_in_square_meters = wiz.film_component_to_treat.product_uom_id._compute_quantity(wiz.film_component_to_treat.product_qty, custom_uom_related_to_surface_uom)
                # 2. compute glue quantity in kg (need component surface)
                glue_qty_in_kg = (wiz.grammage * component_qty_in_square_meters * wiz.coverage_factor) / 1000
                # 3. convert qty in component uom
                kg_uom = self.env.ref('uom.product_uom_kgm')
                wiz.product_qty = kg_uom._compute_quantity(glue_qty_in_kg, wiz.product_uom_id)
            else:
                wiz.product_qty = 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.update({'product_uom_id': self.product_id.uom_id})
        else:
            self.update({'product_uom_id': False})

    def button_add_treatment(self):
        self.ensure_one()
        vals = {
            'bom_id': self.bom_id.id,
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom_id': self.product_uom_id.id,
            'grammage': self.grammage,
            'coverage_factor': self.coverage_factor,
            'film_component_to_treat': self.film_component_to_treat.id if self.film_component_to_treat else False
            }
        return self.env['mrp.bom.line'].create(vals)