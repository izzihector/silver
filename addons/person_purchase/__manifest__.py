# -*- coding: utf-8 -*-
{
    'name': "person Purchase",
    'description': """
       person Purchase
    """,

    'author': "Moahemd abd El Rahman",



    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','website_sale','product_quantity_so_po'],

    # always loaded
    'data': [

        'views/views.xml',
        'security/groups_user.xml',
        'security/ir.model.access.csv',

    ],

}