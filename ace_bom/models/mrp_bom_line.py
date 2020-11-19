# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_round


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    def _default_density_uom_id(self):
        uom = self.env.ref('ace_product.product_uom_density', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_product.product_uom_categ_density')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    # M2m fields
    allowed_uom_ids = fields.Many2many('uom.uom', string='Allowed UoMs', compute='_compute_allowed_uom_ids')

    # M2o fields
    extruder_id = fields.Many2one('mrp.bom.extruder', string='Extruder')
    recipe_bom_line_id = fields.Many2one('mrp.bom.line', string='BoM Recipe Line', readonly=True)
    production_bom_line_ids = fields.One2many('mrp.bom.line', 'recipe_bom_line_id', string='BoM Production Line', readonly=True)

    # Float fields with UoM
    density = fields.Float(string='Density', store=True, related='product_id.density', digits='Product Double Precision')
    density_uom_id = fields.Many2one('uom.uom', string='Density UoM', related='product_id.density_uom_id')
    density_uom_name = fields.Char(string='Density UoM Label', related='density_uom_id.name')

    # Concentration
    layer_concentration = fields.Float(string='Concentration per Layer', digits='BoM Concentration Precision')
    layer_total_concentration = fields.Float(string='Total Concentration per Layer', digits='BoM Concentration Precision', compute='_compute_layer_total_concentration')
    concentration = fields.Float(string='Concentration', digits='BoM Concentration Precision', compute='_compute_concentration')
    related_concentration = fields.Float(string='Recipe Concentration', digits='BoM Concentration Precision', related='recipe_bom_line_id.concentration', help='Concentration taken from recipe line')

    # Char fields
    hopper = fields.Char('Hopper')

    def _compute_allowed_uom_ids(self):
        for line in self:
            if line.bom_id.type == 'recipe':
                categ = self.env.ref('uom.product_uom_categ_kgm')
                uoms = self.env['uom.uom'].search([('category_id', '=', categ.id)])
            else:
                uoms = self.env['uom.uom'].search([])
            line.write({'allowed_uom_ids': [(6, 0, uoms.ids)]})

    @api.depends('layer_concentration', 'extruder_id', 'extruder_id.concentration')
    def _compute_concentration(self):
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
        for line in self:
            precision = self.env['decimal.precision'].precision_get('BoM Concentration Precision')
            line.layer_total_concentration = float_round(sum(line.bom_id.bom_line_ids.filtered(lambda l: l.extruder_id == line.extruder_id).mapped('layer_concentration')), precision_digits=precision)

    def write(self, vals):
        res = super(MrpBomLine, self).write(vals)
        if 'product_id' in vals or 'concentration' in vals or 'extruder_id' in vals:
            for bom in self.bom_id.production_bom_ids:
                bom.activity_schedule(
                    act_type_xmlid='mail.mail_activity_data_warning',
                    date_deadline=fields.Datetime.now(),
                    summary=_('Recipe has changed'),
                    note=_('At least one line of recipe ({}) has changed. You should recompute quantities.').format(self.bom_id.display_name),
                    user_id=self.env.uid)
        return res