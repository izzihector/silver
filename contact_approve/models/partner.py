from odoo import api, fields ,models
from odoo.exceptions import ValidationError 
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit="res.partner"
    state=fields.Selection([('Draft','Draft'),('wait_approve','wait approve'),('Approve','Approve')],default="Draft",string="Status")
    def action_approve(self):
        self.state='Approve'
    def action_wait_approve(self):
        self.state='wait_approve'
class sales_order(models.Model):
    _inherit='sale.order'
    @api.onchange('partner_id')
    def change_partner(self):
        _logger.info("CHANGE PARTNER")
        return {'domain':{'partner_id':[('state','=','Approve')]}}
class purchase_order(models.Model):
    _inherit='purchase.order'
    @api.onchange('partner_id')
    def change_partner(self):
        _logger.info("CHANGE PARTNER")
        return {'domain':{'partner_id':[('state','=','Approve')]}}
class crm_order(models.Model):
    _inherit='crm.lead'
    @api.onchange('partner_id')
    def change_partner(self):
        _logger.info("CHANGE PARTNER")
        return {'domain':{'partner_id':[('state','=','Approve')]}}