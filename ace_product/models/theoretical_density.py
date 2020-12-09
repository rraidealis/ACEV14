# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class TheoreticalDensity(models.Model):
    _name = 'product.theoretical.density'
    _description = 'Product Theoretical Density'

    def _default_density_uom_id(self):
        uom = self.env.ref('ace_data.product_uom_density', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('ace_data.product_uom_categ_density')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'reference')], limit=1)
        return uom

    formula_code_id = fields.Many2one('product.formula.code', string='Formula Code', required=True)
    color_code_id = fields.Many2one('product.color.code', string='Color Code', required=True)
    density = fields.Float(string='Density', required=True)
    density_uom_id = fields.Many2one('uom.uom', string='Density UoM', readonly=True, default=_default_density_uom_id)
    density_uom_name = fields.Char(string='Density UoM Label', related='density_uom_id.name')

    _sql_constraints = [
        ('uniq_color_formula', 'unique(formula_code_id, color_code_id)', 'Combination of formula code and color code should be unique!'),
    ]

    def name_get(self):
        res = []
        for record in self:
            name = '[{}]-[{}]{}-{}'.format(record.formula_code_id.code, record.color_code_id.code, record.color_code_id.color_id.name, record.density)
            res.append((record.id, name))
        return res