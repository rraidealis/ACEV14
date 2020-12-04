# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class UoMTemplate(models.Model):
    _name = 'uom.uom.template'
    _description = 'Product UoM Template'

    name = fields.Char('Unit of Measure', required=True, translate=True)
    category_template_id = fields.Many2one('uom.category.template', string='Category', required=True, ondelete='cascade')
    # required only if type != reference. This is handled in view
    factor_from = fields.Selection(selection='_selection_product_field', string='Ratio From',
                                  help='Value of this product field is used as factor of the new uom. Only float type fields are allowed.')
    factor = fields.Float(
        'Ratio', default=1.0, digits=0, required=True,  # force NUMERIC with unlimited precision
        help='How much bigger or smaller this unit is compared to the reference Unit of Measure for this category: 1 * (reference unit) = ratio * (this unit)')
    user_defined_ratio = fields.Boolean(string='User Defined Ratio', help='Used to manually set a factor instead of using value from a product field')
    rounding = fields.Float(string='Rounding Precision', default=0.01, digits=0, required=True,
        help='The computed quantity will be a multiple of this value. '
             'Use 1.0 for a Unit of Measure that cannot be further split, such as a piece.')
    active = fields.Boolean(string='Active', default=True, help='Uncheck the active field to disable a unit of measure without deleting it.')
    uom_type = fields.Selection([
        ('bigger', 'Bigger than the reference Unit of Measure'),
        ('reference', 'Reference Unit of Measure for this category'),
        ('smaller', 'Smaller than the reference Unit of Measure')], string='Type',
        default='reference', required=1)
    default_uom = fields.Boolean(string='Is Default UoM', default=True, help='This UoM will be used as default UoM on product.')
    default_purchase_uom = fields.Boolean(string='Is Default Purchase UoM', default=True, help='This UoM will be used as default purchase UoM on product.')

    _sql_constraints = [
        ('factor_gt_zero', 'CHECK (factor!=0 OR not user_defined_ratio)', 'The conversion ratio for a unit of measure template cannot be 0.'),
        ('rounding_gt_zero', 'CHECK (rounding>0)', 'The rounding precision must be strictly positive.')
    ]

    def _selection_product_field(self):
        """ return name of all float fields of model product.template """
        model = self.env['ir.model'].search([('model', '=', 'product.template')])
        fields = self.env['ir.model.fields'].search([('ttype', '=', 'float'), ('model_id', '=', model.id)])
        return [(field.name, field.field_description) for field in fields]

    @api.constrains('category_template_id', 'uom_type', 'active')
    def _check_category_reference_uniqueness(self):
        """ Force the existence of only one UoM template reference per category template
            NOTE: this is a constraint on the all table. This might not be a good practice, but this is
            not possible to do it in SQL directly.
        """
        category_template_ids = self.mapped('category_template_id').ids
        self.env['uom.uom.template'].flush(['category_template_id', 'uom_type', 'active'])
        self._cr.execute("""
            SELECT C.id AS category_template_id, count(U.id) AS uom_count
            FROM uom_category_template C
            LEFT JOIN uom_uom_template U ON C.id = U.category_template_id AND uom_type = 'reference' AND U.active = 't'
            WHERE C.id IN %s
            GROUP BY C.id
        """, (tuple(category_template_ids),))
        for uom_data in self._cr.dictfetchall():
            if uom_data['uom_count'] == 0:
                raise ValidationError(_("UoM category template %s should have a reference UoM template. If you just created a new category template, please record the 'reference' unit first.") % (self.env['uom.category.template'].browse(uom_data['category_template_id']).name,))
            if uom_data['uom_count'] > 1:
                raise ValidationError(_("UoM category template %s should only have one reference UoM template.") % (self.env['uom.category.template'].browse(uom_data['category_template_id']).name,))

    @api.constrains('category_template_id')
    def _check_uom_category_template(self):
        """ Prevent existence of more than one reference per category """
        for uom in self:
            reference_uoms = self.env['uom.uom.template'].search([
                ('category_template_id', '=', uom.category_template_id.id),
                ('uom_type', '=', 'reference')])
            if len(reference_uoms) > 1:
                raise ValidationError(_('UoM category template {} should have only one reference UoM template.').format(self.category_template_id.name))

    @api.constrains('default_uom')
    def _check_default_uom(self):
        """
        Prevent existence of more than one default uom per category
        Note: It is not possible to check if there is a least one default uom this way. It should be done like it is done with reference.
        Instead an error will be thrown at uoms creation if there is no default uom.
        """
        for uom in self:
            default_uoms = self.env['uom.uom.template'].search([
                ('category_template_id', '=', uom.category_template_id.id),
                ('default_uom', '=', True)])
            if len(default_uoms) > 1:
                raise ValidationError(_('UoM category template {} should have only one UoM template set as default UoM.').format(self.category_template_id.name))

    @api.constrains('default_purchase_uom')
    def _check_default_purchase_uom(self):
        """
        Prevent existence of more than one default purchase uom per category
        Note: It is not possible to check if there is a least one default purchase uom this way. It should be done like it is done with reference.
        Instead an error will be thrown at uoms creation if there is no default purchase uom.
        """
        for uom in self:
            default_purchase_uoms = self.env['uom.uom.template'].search([
                ('category_template_id', '=', uom.category_template_id.id),
                ('default_purchase_uom', '=', True)])
            if len(default_purchase_uoms) > 1:
                raise ValidationError(_('UoM category template {} should have only one UoM template set as default purchase UoM.').format(self.category_template_id.name))

    @api.onchange('uom_type')
    def _onchange_uom_type(self):
        self.factor_from = False
        self.factor = 1.0
        self.user_defined_ratio = False

    @api.onchange('user_defined_ratio')
    def _onchange_user_defined_ratio(self):
        self.factor = 1.0
        self.factor_from = False
