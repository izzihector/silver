# -*- coding: utf-8 -*-
{
    'name': "activity_message-report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Mohamed abd elrhamn",

    'category': 'mail',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','front_office_management','mail'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
        'views/views.xml',
        #'views/templates.xml',
    ],

}
