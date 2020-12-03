# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class UoMCategoryTemplate(models.Model):
    _name = 'uom.category.template'
    _description = 'Product UoM Category Template'

    name = fields.Char(string='Template Name', required=True, translate=True)
    name_from = fields.Selection(selection='_selection_product_field', required=True, string='Category Name', help='Value of this product field is used as name of the new uom category. Only char fields are allowed.')
    uom_template_ids = fields.One2many('uom.uom.template', 'category_template_id', string='UoM Templates')
    active = fields.Boolean(string='Active', default=True)

    def _selection_product_field(self):
        """ Return name of all char fields of model product.template """
        model = self.env['ir.model'].search([('model', '=', 'product.template')])
        fields = self.env['ir.model.fields'].search([('ttype', '=', 'char'), ('model_id', '=', model.id)])
        return [(field.name, field.field_description) for field in fields]

    @api.constrains('uom_template_ids')
    def _check_uom_template_ids(self):
        """ Check if there is at least one uom reference for current category """
        for category in self:
            uoms = category.uom_template_ids.filtered(lambda uom: uom.uom_type == 'reference')
            if len(uoms) < 1:
                raise ValidationError(_('UoM category template {} should have at least one UoM template set as "reference" unit.').format(category.name))
