import logging 
from odoo import fields, http, tools, _
from odoo.http import request
_logger = logging.getLogger(__name__)
from odoo import api, fields ,models
from odoo.exceptions import ValidationError 
from odoo.http import request

class order(models.Model):
    _inherit="res.users"
    @api.constrains("partner_id")
    def get_partner(self):
        if self.partner_id:
            partner_ids=self.env["res.users"].search([('partner_id','=',self.partner_id.id)])
            _logger.info("FFFFF")
            _logger.info(partner_ids)
            _logger.info(self.partner_id.id)
            if len(partner_ids)>1:
                raise ValidationError("You can't create two user to the same customer")
   

