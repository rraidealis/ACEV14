# -*- coding: utf-8 -*-
{
    'name': 'ACE UoM Management',
    'version': '14.0.0.1',
    'category': 'Sales/Sales',
    'summary': '',
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['ace_product'],
    'data': [
		'security/ir.model.access.csv',
        'views/uom_category_template_views.xml',
        'views/uom_uom_template_views.xml',
        'views/product_views.xml',
        'views/product_category_views.xml'
	],
    'auto_install': False,
    'installable': True,
    'application': False,
}

