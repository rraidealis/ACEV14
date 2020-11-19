# -*- coding: utf-8 -*-
{
    'name': 'ACE BoM Management',
    'version': '14.0.0.1',
    'category': 'Manufacturing/Manufacturing',
    'summary': '',
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['ace_product'],
    'data': [
		'security/ir.model.access.csv',
        'data/bom_data.xml',
        'views/mrp_bom_views.xml',
        'wizard/import_recipe_views.xml'
	],
    'auto_install': False,
    'installable': True,
    'application': True,
}

