# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools import float_compare, float_round


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
    product_uom_id = fields.Many2one('uom.uom', string='Final Product Unit of Measure', default=_get_default_product_uom_id)
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
                    wiz.coverage_factor = (wiz.product_id.width / wiz.bom_id.total_production_width) * 100

    @api.depends('bom_id.total_production_width', 'product_id', 'is_manual_border_factor', 'manual_border_factor')
    def _compute_border_factor(self):
        """
        Compute border factor of a component according to production width set on parent BoM and product width.
        If value is below 0.0 then return 0.0
        Note: production width and product width are in the same UOM
        """
        precision = self.env['decimal.precision'].precision_get('Product Double Precision')
        for wiz in self:
            wiz.border_factor = 0.0
            if wiz.is_manual_border_factor:
                wiz.border_factor = wiz.manual_border_factor
            elif wiz.bom_id.total_production_width and wiz.product_id and wiz.product_id.width:
                border_factor = ((wiz.product_id.width - wiz.bom_id.total_production_width) / wiz.bom_id.total_production_width) * 100
                wiz.border_factor = border_factor if float_compare(border_factor, 0.0, precision_digits=precision) > 0 else 0.0

    @api.depends('product_id.total_grammage', 'coverage_factor', 'border_factor', 'stretching_factor')
    def _compute_grammage(self):
        """
        Compute grammage of a component according to product total grammage,
        coverage factor, border factor and stretching factor
        If value is below 0.0 then return 0.0
        """
        precision = self.env['decimal.precision'].precision_get('Product Single Precision')
        for wiz in self:
            wiz.grammage = 0.0
            if wiz.product_id and wiz.product_id.total_grammage and wiz.coverage_factor and wiz.stretching_factor:
                grammage = (wiz.product_id.total_grammage * ((wiz.coverage_factor - wiz.border_factor) / 100)) - ((wiz.product_id.total_grammage * ((wiz.coverage_factor - wiz.border_factor) / 100)) * (wiz.stretching_factor / 100))
                wiz.grammage = grammage if float_compare(grammage, 0.0, precision_digits=precision) > 0 else 0.0

    @api.depends('proxy_product_uom_id', 'stretching_factor', 'bom_id')
    def _compute_product_qty(self):
        for wiz in self:
            if wiz.stretching_factor and wiz.product_id and wiz.proxy_product_uom_id:
                # retrieve all uoms in the same category than product length uom
                all_length_uoms = self.env['uom.uom'].search([('category_id', '=', wiz.product_id.length_uom_id.category_id.id)])
                # retrieve an UoM linked to one of those uoms and in the same category than the wizard product
                custom_uom_related_to_length_uom = self.env['uom.uom'].search([('category_id', '=', wiz.product_id.uom_id.category_id.id), ('related_uom_id', 'in', all_length_uoms.ids)], limit=1)
                if custom_uom_related_to_length_uom:
                    # compute quantity according to product length and stretching factor
                    product_quantity = wiz.product_id.ace_length - (wiz.product_id.ace_length * (wiz.stretching_factor / 100))
                    # convert result from the length uom to the one linked to the custom uom
                    product_qty_in_length_unit = wiz.product_id.length_uom_id._compute_quantity(product_quantity, custom_uom_related_to_length_uom.related_uom_id)
                    # in order to update product quantity if uom changes, we use a proxy to keep track of previous uoms:
                    # 1. convert into the previous uom (in case user changes proxy_product_uom_id)
                    product_qty_in_previous_uom = custom_uom_related_to_length_uom._compute_quantity(product_qty_in_length_unit, wiz.product_uom_id)
                    # 2. than convert into the right uom (proxy_product_uom_id)
                    wiz.product_qty = wiz.product_uom_id._compute_quantity(product_qty_in_previous_uom, wiz.proxy_product_uom_id)
                    # 3. finally update the previous uom
                    wiz.product_uom_id = wiz.proxy_product_uom_id

                    # Product quantity depends on quantity to produce.
                    # We have to multiply product quantity by quantity set on parent BoM
                    if wiz.bom_id and wiz.bom_id.product_qty and wiz.bom_id.product_uom_id:
                        # convert to reference
                        uom_category = wiz.bom_id.product_uom_id.category_id
                        uom_reference = self.env['uom.uom'].search([('category_id', '=', uom_category.id), ('uom_type', '=', 'reference')])
                        if uom_reference:
                            precision = self.env['decimal.precision'].precision_get('Product Double Precision')
                            reference_qty = wiz.bom_id.product_uom_id._compute_quantity(wiz.bom_id.product_qty, uom_reference)
                            # multiply by reference
                            component_qty = float_round(wiz.product_qty * reference_qty, precision_digits=precision)
                            # convert from reference to BoM product UoM
                            wiz.product_qty = uom_reference._compute_quantity(component_qty, wiz.bom_id.product_uom_id)
                else:
                    wiz.product_qty = 0.0
                    wiz.product_uom_id = wiz.proxy_product_uom_id
            else:
                wiz.product_qty = 0.0
                wiz.product_uom_id = wiz.proxy_product_uom_id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
                self.product_uom_id = self.product_id.uom_id
                self.proxy_product_uom_id = self.product_id.uom_id
        else:
            self.product_uom_id = False
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

