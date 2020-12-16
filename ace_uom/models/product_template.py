# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    show_banner_missing_uom = fields.Boolean(string='Show Banner Missing UoM', compute='_compute_custom_uom_banner_and_button_visibility', help='Used to display a banner if custom uoms have not yet been computed')
    show_generate_uoms_button = fields.Boolean(string='Show Generate UoMs Button', compute='_compute_custom_uom_banner_and_button_visibility', help='Used to show "generate UoMs" button if custom uoms are in use for current product')

    @api.depends(
        'categ_id.uom_category_template_id',
        'uom_id.uom_template_id',
        'uom_po_id.uom_template_id',
        'sale_ok',
        'purchase_ok',
        'active'
        )
    def _compute_custom_uom_banner_and_button_visibility(self):
        """
        Banner 'missing uoms' should be visible if:
        - product is active
        - product's category has an UoM category template set
        - product uom OR product purchase uom has no UoM template
        In case of missing uoms, sale and purchase should not be allowed

        Button 'generate uoms' should be visible if:
        - product is active
        - product's category has an UoM category template set
        """
        for product in self:
            product.show_banner_missing_uom = False
            product.show_generate_uoms_button = False
            if product.active and product.categ_id.uom_category_template_id:
                product.show_generate_uoms_button = True
                if not (product.uom_id.uom_template_id and product.uom_po_id.uom_template_id):
                    product.update({'show_banner_missing_uom': True, 'sale_ok': False, 'purchase_ok': False})

    def generate_uoms_action(self):
        """
        Generate uoms if product category is set to handle uom templates.
        Note: This action may be called several times
        1. Check if there is an uom category template set on product category then,
        2. Retrieve uom category from uom_id
        2a. If uom_id category has been created from a template and this template is the same
            as the one set on product category then keep reference and archives the other ones
        2b. Else try to create a new uom category with information from uom category template. If category name is
            not valid or is already in use, then raise an error
        3. Look for duplicates or non-existence of reference, default uom and default purchase uom in uom templates
        4. If a reference has been kept, update it, else create a new one from template
        5. Create other uoms. This should be done only if there is one reference unit.
        6. Updates uom_id and uom_po_id on product with recently created uoms
        """
        self.ensure_one()
        category_template = self.categ_id.uom_category_template_id
        # 1. Check if there is an uom category template set on product category
        if category_template:
            # 2. Retrieve category name from product field value and look for a matching record in database
            category_name = getattr(self, category_template.name_from)
            if not category_name:
                raise ValidationError(_('Unable to create a new UoM category with this name (field name: {}, field value: {}).').format(category_template.name_from, category_name))
            default_uom_category = self.env['uom.category'].search([('name', '=', category_name)], limit=1)
            # 2a. If there is already a category with this name and this category has the same template than the one set on product category
            #     then keep reference and archive other uoms
            if default_uom_category:
                if default_uom_category.category_template_id and default_uom_category.category_template_id == category_template:
                    uoms = self.env['uom.uom'].search([('category_id', '=', default_uom_category.id), ('active', '=', True)])
                    reference_uom = uoms.filtered(lambda uom: uom.uom_type == 'reference')
                    (uoms - reference_uom).write({'active': False})
                else:
                    raise ValidationError(_('There is already an UoM category with this name ({}).').format(category_name))
            # 2b. Else create a new category
            else:
                default_uom_category = self.env['uom.category'].create({'name': category_name, 'category_template_id': category_template.id})
                reference_uom = self.env['uom.uom']
            # 3. Look for duplicates or non-existence of reference, default uom and default purchase uom in uom templates
            reference_uom_template = category_template.uom_template_ids.filtered(lambda x: x.uom_type == 'reference')
            default_uom_template = category_template.uom_template_ids.filtered(lambda x: x.default_uom)
            default_uom_po_template = category_template.uom_template_ids.filtered(lambda x: x.default_purchase_uom)
            if len(reference_uom_template) != 1:
                raise ValidationError(_('Category template {} should have one "reference" uom template (found {}).').format(category_template.name, len(reference_uom_template)))
            if len(default_uom_template) != 1:
                raise ValidationError(_('Category template {} should have one "default" uom template (found {}).').format(category_template.name, len(default_uom_template)))
            if len(default_uom_po_template) != 1:
                raise ValidationError(_('Category template {} should have one "default purchase" uom template (found {}).').format(category_template.name, len(default_uom_po_template)))
            # 4. If a reference has been kept, update it, else create a new one from template
            if not reference_uom:
                reference_uom = self.env['uom.uom'].create(self._prepare_uom_values(reference_uom_template, default_uom_category))
            else:
                reference_uom.write({
                    'name': reference_uom_template.name,
                    'category_id': default_uom_category.id,
                    'rounding': reference_uom_template.rounding,
                    'uom_template_id': reference_uom_template.id})
            # 5. Create other uoms. This should be done only if there is one reference unit
            for uom_template in (category_template.uom_template_ids - reference_uom_template):
                self.env['uom.uom'].create(self._prepare_uom_values(uom_template, default_uom_category))
            # 6. Updates uom_id and uom_po_id on product with recently created uoms
            default_uom = self.env['uom.uom'].search([('uom_template_id', '=', default_uom_template.id), ('category_id', '=', default_uom_category.id), ('active', '=', True)])
            default_uom_po = self.env['uom.uom'].search([('uom_template_id', '=', default_uom_po_template.id), ('category_id', '=', default_uom_category.id), ('active', '=', True)])
            self.write({'uom_id': default_uom.id, 'uom_po_id': default_uom_po.id})
            # 7. Post message
            self.message_post(body=_("New UoMs have been generated"))

    def _prepare_uom_values(self, template, category):
        """
        Prepare uom values from uom template and uom category
        If factor is not different than 0.0, raise an error
        """
        if template.uom_type == 'reference':
            factor = 1.0
        else:
            if template.factor_from and not template.user_defined_ratio:
                factor = getattr(self, template.factor_from)
            elif template.factor and template.user_defined_ratio:
                factor = template.factor
            else:
                raise ValidationError(_('Unable to create UoM {}: conversion ratio is missing.').format(template.name))
        if float_compare(factor, 0.000, 3) == 0:
            raise ValidationError(_('Cannot create an uom with a factor equal to 0.0 (field name: {}, field value: {}).').format(template.factor_from, factor))
        return {
            "name": template.name,
            "category_id": category.id,
            "rounding": template.rounding,
            "uom_type": template.uom_type,
            "uom_template_id": template.id,
            "factor": factor,
        }
