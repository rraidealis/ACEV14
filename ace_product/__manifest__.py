# -*- coding: utf-8 -*-
{
    'name': 'Ace Product & Inventory',
    'version': '14.0.0.3',
    'category': 'Operations/Inventory',
    'summary': '',
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['mrp'],
    'data': [
		'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/mrp_bom_views.xml',
        'views/product_category_views.xml',
        'views/product_menu_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

