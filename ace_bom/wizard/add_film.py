# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class AddFilm(models.TransientModel):
    _name = 'mrp.bom.add.film'
    _description = 'Add Film type product to BoM components of a Glued Film'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    def _default_grammage_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_grammage', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_data.product_uom_categ_grammage')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    allowed_category_type = fields.Char(string='Product Category Type')
    allowed_product_category_ids = fields.Many2many('product.category', string='Allowed Categories', compute='_compute_allowed_product_category_ids')
    product_id = fields.Many2one('product.product', string='Component', required=True)
    product_qty = fields.Float(string='Quantity', compute='_compute_product_qty', digits='Product Unit of Measure')
    product_uom_id = fields.Many2one('uom.uom', string='Final Product Unit of Measure', compute='_compute_product_uom_id')
    proxy_product_uom_id = fields.Many2one('uom.uom', string='Product Unit of Measure', default=_get_default_product_uom_id,
                                     required=True,
                                     help='Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control',
                                     domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    bom_id = fields.Many2one('mrp.bom', string='Production BoM', required=True)
    grammage = fields.Float(string='Grammage', store=True, compute='_compute_grammage', digits='Product Single Precision')
    grammage_uom_id = fields.Many2one('uom.uom', string='Grammage UoM', readonly=True, default=_default_grammage_uom_id)
    grammage_uom_name = fields.Char(string='Grammage UoM Label', related='grammage_uom_id.name')
    coverage_factor = fields.Float(string='Coverage Factor', store=True, compute='_compute_coverage_factor', digits='Product Double Precision')
    stretching_factor = fields.Float(string='Stretching Factor', digits='Product Double Precision', default=0.0)
    border_factor = fields.Float(string='Border Factor', store=True, compute='_compute_border_factor', digits='Product Double Precision')
    manual_border_factor = fields.Float(string='Manual Border Factor', digits='Product Double Precision')
    is_manual_border_factor = fields.Boolean(string='User Defined Border Factor')

    @api.depends('proxy_product_uom_id')
    def _compute_product_uom_id(self):
        for wiz in self:
            wiz.product_uom_id = wiz.proxy_product_uom_id

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

    @api.depends('bom_id.total_production_width', 'product_id.width', 'product_id.categ_id')
    def _compute_coverage_factor(self):
        """
        Compute coverage factor of a component according to production width set on parent BoM and product width
        Note: production width and product width are in the same UOM
        """
        for wiz in self:
            wiz.coverage_factor = 0.0
            if wiz.product_id:
                if wiz.product_id.categ_id.is_film and wiz.bom_id.total_production_width and wiz.product_id.width:
                    wiz.coverage_factor = wiz.product_id.width / wiz.bom_id.total_production_width

    @api.depends('bom_id.total_production_width', 'product_id', 'is_manual_border_factor', 'manual_border_factor')
    def _compute_border_factor(self):
        """
        Compute border factor of a component according to production width set on parent BoM and product width.
        If value is below 0.0 then return 0.0
        Note: production width and product width are in the same UOM
        """
        for wiz in self:
            wiz.border_factor = 0.0
            if wiz.is_manual_border_factor:
                wiz.border_factor = wiz.manual_border_factor
            elif wiz.bom_id.total_production_width and wiz.product_id and wiz.product_id.width:
                border_factor = (wiz.product_id.width - wiz.bom_id.total_production_width) / wiz.bom_id.total_production_width
                wiz.border_factor = border_factor if border_factor > 0 else 0.0

    @api.depends('product_id.total_grammage', 'coverage_factor', 'border_factor', 'stretching_factor')
    def _compute_grammage(self):
        """
        Compute grammage of a component according to product total grammage,
        coverage factor, border factor and stretching factor
        If value is below 0.0 then return 0.0
        """
        for wiz in self:
            wiz.grammage = 0.0
            if wiz.product_id and wiz.product_id.total_grammage and wiz.coverage_factor:
                coverage_minus_border = wiz.coverage_factor - wiz.border_factor
                if wiz.stretching_factor:
                    grammage = (wiz.product_id.total_grammage * coverage_minus_border) - (wiz.product_id.total_grammage * coverage_minus_border * wiz.stretching_factor)
                else:
                    grammage = wiz.product_id.total_grammage * coverage_minus_border
                wiz.grammage = grammage if grammage > 0 else 0.0

    @api.depends('proxy_product_uom_id', 'stretching_factor', 'bom_id')
    def _compute_product_qty(self):
        for wiz in self:
            if wiz.bom_id and wiz.bom_id.product_tmpl_id and wiz.product_id and wiz.proxy_product_uom_id:
                # 1. Retrieving quantity to produce in meters
                # retrieve uom related to meters
                meters_uom = self.env.ref('uom.product_uom_meter')
                custom_uom_related_to_meters = self.env['uom.uom'].search([('category_id', '=', wiz.bom_id.product_uom_id.category_id.id), ('related_uom_id', '=', meters_uom.id)], limit=1)
                # convert quantity to produce in this uom
                if custom_uom_related_to_meters:
                    qty_to_produce_in_meters = wiz.bom_id.product_uom_id._compute_quantity(wiz.bom_id.product_qty, custom_uom_related_to_meters)
                else:
                    qty_to_produce_in_meters = 0.0

                # 2. Applying stretching factor if any
                if wiz.stretching_factor:
                    stretched_qty_to_produce_in_meters = qty_to_produce_in_meters - (qty_to_produce_in_meters * wiz.stretching_factor)
                else:
                    stretched_qty_to_produce_in_meters = qty_to_produce_in_meters

                # 3. Converting stretched quantity in the same uom as the component one
                # retrieve an UoM linked to a length UoM and in the same category than the component UoM category
                custom_uom_related_to_meters = self.env['uom.uom'].search([('category_id', '=', wiz.product_id.uom_id.category_id.id), ('related_uom_id', '=', meters_uom.id)], limit=1)
                if custom_uom_related_to_meters:
                    wiz.product_qty = custom_uom_related_to_meters._compute_quantity(stretched_qty_to_produce_in_meters, wiz.proxy_product_uom_id)
                else:
                    wiz.product_qty = 0.0
            else:
                wiz.product_qty = 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.proxy_product_uom_id = self.product_id.uom_id
        else:
            self.proxy_product_uom_id = False

    def button_add_film(self):
        self.ensure_one()
        vals = {
            'bom_id': self.bom_id.id,
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom_id': self.product_uom_id.id,
            'grammage': self.grammage,
            'coverage_factor': self.coverage_factor,
            'stretching_factor': self.stretching_factor,
            'border_factor': self.border_factor,
            }
        return self.env['mrp.bom.line'].create(vals)

