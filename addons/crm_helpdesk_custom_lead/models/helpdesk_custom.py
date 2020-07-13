from odoo import api, fields, models, _

class crm_help(models.TransientModel):
    _inherit='crm.lead.convert2ticket'
    def action_lead_to_helpdesk_ticket(self):
        self.ensure_one()
        # get the lead to transform
        lead = self.lead_id
        partner_id = self._find_matching_partner()
        if not partner_id and (lead.partner_name or lead.contact_name):
            partner_id = lead.handle_partner_assignation()[lead.id]
        # create new helpdesk.ticket
        
        vals = {
            "name": lead.name,
            "description": lead.description,
            "email": lead.email_from,
            "lead_id":self.lead_id.id,
            "team_id": self.team_id.id,
             
            "ticket_type_id": self.ticket_type_id.id,
            "partner_id": partner_id,
            "user_id": None
        }
        ticket = self.env['helpdesk.ticket'].create(vals)
        # move the mail thread
        lead.message_change_thread(ticket)
        # move attachments
        attachments = self.env['ir.attachment'].search([('res_model', '=', 'crm.lead'), ('res_id', '=', lead.id)])
        attachments.sudo().write({'res_model': 'helpdesk.ticket', 'res_id': ticket.id})
        # archive the lead
        #lead.write({'active': False})
        # return the action to go to the form view of the new Ticket
        view = self.env.ref('helpdesk.helpdesk_ticket_view_form')
        return {
            'name': _('Ticket created'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'res_id': ticket.id,
            'context': self.env.context
        }
class ticket(models.Model):
    _inherit='helpdesk.ticket'
    lead_id = fields.Many2one('crm.lead', string='Lead', domain=[('type', '=', 'lead')])
    count_order=fields.Integer("count Order")
    count_lead=fields.Integer("Count Leads")
    count_sheet=fields.Integer("Count Survey Sheet")
    survey_team=fields.Boolean("Survey sheet")
    @api.onchange("team_id")
    def get_change_team(self):
        if self.team_id:
            self.survey_team=self.team_id.survey_team
    @api.constrains("team_id")
    def get_save_team(self):
        if self.team_id:
            self.survey_team=self.team_id.survey_team
    def create_lead(self):
        view = self.env.ref('crm.crm_lead_view_form')
         
        return {
            'name': _('Lead'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'context':{'default_ticket_id': self.id,'default_name':self.name,'default_partner_id':self.partner_id.id,'default_user_id':self.user_id.id},
            'target':'current'
        }
    def action_view_leads(self):
        view = self.env.ref('crm.crm_case_tree_view_leads')
        view_form=self.env.ref('crm.crm_lead_view_form')
        orders=self.env['crm.lead'].search([('ticket_id','=',self.id)])
        ids=[]
        for rec in orders:
            ids.append(rec.id)
        return {
            'name': _('leads'),
            'view_mode': 'tree,form',
            'view_type':'form',
            'views': [(view.id,'tree'),(view_form.id,'form')],
            'res_model': 'crm.lead',
            'domain':[('id','in',ids)],
            'type': 'ir.actions.act_window',
            'target':'current'
        }
    @api.constrains("lead_id")
    def get_count(self):
        if self.lead_id:
            self.lead_id.count_lead+=1
    def create_sale_order(self):
        view = self.env.ref('sale.view_order_form')
        context=''
        if self.partner_id:
            context={'default_partner_id': self.partner_id.id}
        return {
            'name': _('Sales Order'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'context':{'default_partner_id': self.partner_id.id,'default_lead_id':self.lead_id.id,'default_ticket_id':self.id},
            'target':'current'
        }
    def action_view_sale_order(self):
        view = self.env.ref('sale.view_quotation_tree')
        view_form=self.env.ref('sale.view_order_form')
        orders=self.env['sale.order'].search([('ticket_id','=',self.id)])
        ids=[]
        for rec in orders:
            ids.append(rec.id)
        return {
            'name': _('Sales Order'),
            'view_mode': 'tree,form',
            'view_type':'form',
            'views': [(view.id,'tree'),(view_form.id,'form')],
            'res_model': 'sale.order',
            'domain':[('id','in',ids)],
            'type': 'ir.actions.act_window',
            'target':'current'
        }
    def create_survey_sheet(self):
        view = self.env.ref('crm_helpdesk_custom_lead.survey_sheet_view_form')
         
        return {
            'name': _('Survey Sheet'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'survey.sheet',
            'type': 'ir.actions.act_window',
            'context':{'default_ticket_id': self.id},
            'target':'current'
        }
    def action_view_survey_sheet(self):
        view = self.env.ref('crm_helpdesk_custom_lead.survey_sheet_view_tree')
        view_for=self.env.ref('crm_helpdesk_custom_lead.survey_sheet_view_form')
        orders=self.env['survey.sheet'].search([('ticket_id','=',self.id)])
        ids=[]
        for rec in orders:
            ids.append(rec.id)
        return {
            'name': _('Survey Sheet'),
            'view_mode': 'tree,form',
            'view_type':'form',
            'views': [(view.id,'tree'),(view_for.id,'form')],
            'res_model': 'survey.sheet',
            'domain':[('id','in',ids)],
            'type': 'ir.actions.act_window',
            'target':'current'
        }

class sales_cus(models.Model):
    _inherit='sale.order'
    lead_id = fields.Many2one('crm.lead', string='Lead')
    ticket_id= fields.Many2one('helpdesk.ticket', string='Ticket')
    
    @api.constrains("ticket_id")
    def get_count(self):
        if self.ticket_id:
            self.ticket_id.count_order+=1
            value={
            'body':"create by ticket  " +self.ticket_id.name ,
            'res_id':self.id,
            'model':'sale.order',
            'message_type':'notification',
            }
            self.message_ids.create(value)
    @api.constrains("opportunity_id")
    def get_count_op(self):
        if self.opportunity_id:
            self.opportunity_id.count_order+=1
            value={
            'body':"create by ticket  " +self.opportunity_id.name ,
            'res_id':self.id,
            'model':'sale.order',
            'message_type':'notification',
            }
            self.message_ids.create(value)
         
    
        
class ticket(models.Model):
    _inherit='crm.lead'
    count_lead=fields.Integer("Count Lead")
    ticket_id=fields.Many2one("helpdesk.ticket",string="ticket")
    count_order=fields.Integer("Count Order")
    def action_view_sale_order(self):
        action = self.env.ref('sale.action_orders').read()[0]
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id,
        }
        action['domain'] = ['|',('opportunity_id', '=', self.id), ('lead_id','=',self.id)]
        orders = self.mapped('order_ids').filtered(lambda l: l.state not in ('draft', 'sent', 'cancel'))
        if len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.id
        return action
     
    """def action_view_sale_order(self):
        view = self.env.ref('sale.view_quotation_tree')
        view_form=self.env.ref('sale.view_order_form')
        orders=self.env['sale.order'].search(['|',('opportunity_id','=',self.id),('lead_id','=',self.id)])
        ids=[]
        for rec in orders:
            ids.append(rec.id)
        return {
            'name': _('Sales Order'),
            'view_mode': 'tree,form',
            'view_type':'form',
            'views': [(view.id,'tree'),(view_form.id,'form')],
            'res_model': 'sale.order',
            'domain':[('id','in',ids)],
            'type': 'ir.actions.act_window',
            'target':'current'
        }"""
     
    @api.constrains("ticket_id")
    def get_ticket_lead(self):
        if self.ticket_id:
            self.ticket_id.count_lead+=1
             
        value={}
        value={
        'body':"created by ticket  " +self.ticket_id.name ,
        'res_id':self.id,
        'model':'crm.lead',
        'message_type':'notification',
        }
        self.message_ids.create(value)
    def action_view_ticketes(self):
        view = self.env.ref('helpdesk.helpdesk_tickets_view_tree')
        view_form=self.env.ref('helpdesk.helpdesk_ticket_view_form')
        orders=self.env['helpdesk.ticket'].search([('lead_id','=',self.id)])
        ids=[]
        for rec in orders:
            ids.append(rec.id)
        return {
            'name': _('Tickets'),
            'view_mode': 'tree,form',
            'view_type':'form',
            'views': [(view.id,'tree'),(view_form.id,'form')],
            'res_model': 'helpdesk.ticket',
            'domain':[('id','in',ids)],
            'type': 'ir.actions.act_window',
            'target':'current'
        }


class survey_sheet(models.Model):
    _name='survey.sheet'
    _description='Survey sheet'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    survey_line=fields.One2many("survey.sheet.line","suvery_sheet",String="Locations")
    name=fields.Char("Name")
    ticket_id=fields.Many2one("helpdesk.ticket",string="ticket")
    help_team=fields.Many2one("related=ticket_id.team_id","Team")
    message_follower_ids=fields.One2many("mail.followers","res_id",String="Followers")
    activity_ids=fields.One2many("mail.activity","res_id",String="Activity")
    message_ids=fields.One2many("mail.message","res_id",String="message")
    state=fields.Selection([('draft','Draft'),('approve','Approve')],String="Status",default='draft')
    lighting=fields.Integer("Lighting On/OFF")
    Lighting_dimming=fields.Integer("Lighting Dimming")
    Curtains=fields.Integer("Curtains")
    AC=fields.Integer("AC")
    Keypad=fields.Integer("Keypad")
    DLP=fields.Integer("DLP")
    Sensors=fields.Integer("Sensors")
    Speakers=fields.Integer("Speakers")
    @api.constrains("survey_line")
    def get_survey_details(self):
        lighting,Lighting_dimming,Curtains,AC,Keypad,DLP,Sensors,Speakers=0,0,0,0,0,0,0,0
        for rec in self.survey_line:
            lighting+=rec.lighting
            Lighting_dimming+=rec.Lighting_dimming
            Curtains+=rec.Curtains
            AC+=rec.AC
            Keypad+=rec.Keypad
            DLP+=rec.DLP
            Sensors+=rec.Sensors
            Speakers+=rec.Speakers
       

        self.lighting=lighting
        self.Lighting_dimming=Lighting_dimming
        self.Curtains=Curtains
        self.AC=AC
        self.Keypad=Keypad
        self.DLP=DLP
        self.Sensors=Sensors
        self.Speakers=Speakers







    
    def action_draft(self):
        self.state='approve'
    @api.constrains("ticket_id")
    def get_count(self):
        if self.ticket_id:
            self.ticket_id.count_sheet+=1
            value={
            'body':"create by ticket  " +self.ticket_id.name ,
            'res_id':self.id,
            'model':'survey.sheet',
            'message_type':'notification',
            }
            self.message_ids.create(value)
class survey_sheet_line(models.Model):
    _name='survey.sheet.line'
    suvery_sheet=fields.Many2one("survey sheet")
    name=fields.Many2one("survey.sheet.location",String="Location")
    lighting=fields.Integer("Lighting On/OFF")
    notes=fields.Char("Notes")
    Lighting_dimming=fields.Integer("Lighting Dimming")
    Curtains=fields.Integer("Curtains")
    AC=fields.Integer("AC")
    Keypad=fields.Integer("Keypad")
    DLP=fields.Integer("DLP")
    Sensors=fields.Integer("Sensors")
    Speakers=fields.Integer("Speakers")
    

class helpdesk_team(models.Model):
    _inherit='helpdesk.team'
    survey_team=fields.Boolean("Survey Team")
class loction(models.Model):
    _name="survey.sheet.location"
    name=fields.Char("Location Name")
