# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ##############
    # New Fields #
    ##############

    # M2o fields
    packaging_bom_id = fields.Many2one('mrp.bom', string='Packing Norm', domain=[('type', '=', 'packaging')])
    stretch_program_id = fields.Many2one('product.stretch.program', string='Stretch Program', compute='_compute_packing_fields', store=True)
    pallet_type_id = fields.Many2one('product.pallet.type', string='Pallet Type')

    # Boolean fields
    is_package_stored = fields.Boolean(string='Storage by Package')

    # Selection fields
    coil_position = fields.Selection([('vertical', 'Vertical'), ('horizontal', 'Horizontal')], string='Coil Position', compute='_compute_packing_fields', store=True)

    # Integer fields with units
    coil_by_pallet = fields.Integer(string='Coil by Pallet', compute='_compute_packing_fields', store=True)
    coil_by_pallet_uom_id = fields.Many2one('uom.uom', string='Coil by Pallet UoM', compute='_compute_packing_fields', store=True)
    coil_by_pallet_uom_name = fields.Char(string='Coil by Pallet UoM Label', related='coil_by_pallet_uom_id.name')

    coil_by_layer = fields.Integer(string='Coil by Layer', compute='_compute_packing_fields', store=True)
    coil_by_layer_uom_id = fields.Many2one('uom.uom', string='Coil by Layer UoM', compute='_compute_packing_fields', store=True)
    coil_by_layer_uom_name = fields.Char(string='Coil by Layer UoM Label', related='coil_by_layer_uom_id.name')

    layer_number = fields.Integer(string='Number of Layers', compute='_compute_packing_fields', store=True)
    layer_number_uom_id = fields.Many2one('uom.uom', string='Number of Layers UoM', compute='_compute_packing_fields', store=True)
    layer_number_uom_name = fields.Char(string='Number of Layers UoM Label', related='layer_number_uom_id.name')

    coil_by_package = fields.Integer(string='Coil by Package', compute='_compute_packing_fields', store=True)
    coil_by_package_uom_id = fields.Many2one('uom.uom', string='Coil by Package UoM', compute='_compute_packing_fields', store=True)
    coil_by_package_uom_name = fields.Char(string='Coil by Package UoM Label', related='coil_by_package_uom_id.name')

    # Form visibility
    show_packing_norm = fields.Boolean(string='Show Packing Norm', related='categ_id.show_packing_norm')
    show_stretch_program = fields.Boolean(string='Show Stretch Program', related='categ_id.show_stretch_program')
    show_pallet_type = fields.Boolean(string='Show Pallet Type', related='categ_id.show_pallet_type')
    show_is_package_stored = fields.Boolean(string='Show Storage by Package', related='categ_id.show_is_package_stored')
    show_coil_position = fields.Boolean(string='Show Coil Position', related='categ_id.show_coil_position')
    show_coil_by_pallet = fields.Boolean(string='Show Coil by Pallet', related='categ_id.show_coil_by_pallet')
    show_coil_by_package = fields.Boolean(string='Show Coil by Package', related='categ_id.show_coil_by_package')
    show_coil_by_layer = fields.Boolean(string='Show Coil by Layer', related='categ_id.show_coil_by_layer')
    show_layer_number = fields.Boolean(string='Show Number of Layers', related='categ_id.show_layer_number')

    ####################
    # Computed Methods #
    ####################
    @api.depends('packaging_bom_id',
                 'packaging_bom_id.stretch_program_id',
                 'packaging_bom_id.coil_position',
                 'packaging_bom_id.coil_by_pallet',
                 'packaging_bom_id.coil_by_pallet_uom_id',
                 'packaging_bom_id.coil_by_layer',
                 'packaging_bom_id.coil_by_layer_uom_id',
                 'packaging_bom_id.layer_number',
                 'packaging_bom_id.layer_number_uom_id',
                 'packaging_bom_id.coil_by_package',
                 'packaging_bom_id.coil_by_package_uom_id')
    def _compute_packing_fields(self):
        for product in self:
            packaging_bom = product.packaging_bom_id
            product.stretch_program_id = packaging_bom.stretch_program_id if packaging_bom else False
            product.coil_position = packaging_bom.coil_position if packaging_bom else False
            product.coil_by_pallet = packaging_bom.coil_by_pallet if packaging_bom else 0
            product.coil_by_pallet_uom_id = packaging_bom.coil_by_pallet_uom_id if packaging_bom else False
            product.coil_by_layer = packaging_bom.coil_by_layer if packaging_bom else 0
            product.coil_by_layer_uom_id = packaging_bom.coil_by_layer_uom_id if packaging_bom else False
            product.layer_number = packaging_bom.layer_number if packaging_bom else 0
            product.layer_number_uom_id = packaging_bom.layer_number_uom_id if packaging_bom else False
            product.coil_by_package = packaging_bom.coil_by_package if packaging_bom else 0
            product.coil_by_package_uom_id = packaging_bom.coil_by_package_uom_id if packaging_bom else False
