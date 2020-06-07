
{
    'name': 'helpdesk  & crm custom ',
    'version': '1.3',
    'category': 'helpdesk',
    'description': """create sales order from ticket  and relate between ticket and lead 
""",
    'depends': ['crm', 'helpdesk','crm_helpdesk','sale','base_setup',
        'sales_team',
        'mail',
        'calendar',
        'resource',
        'fetchmail',
        'utm',
        'web_tour',
        'contacts',
        'digest',
        'phone_validation',],
    'data': ['views/ticket_sale.xml','views/survey_sheet.xml','secuirty/ir.model.access.csv'],
     
    'installable': True,
    'auto_install': True,
}
