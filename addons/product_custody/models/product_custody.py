from odoo import api, fields, models, exceptions ,_
from datetime import date
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)
class ProductCustody(models.Model):
    _name= "product.custody"
    _inherit = ['mail.thread']

    name = fields.Char(string='Custody #', size=64, readonly=True, default=lambda *a: '/')
    product_id = fields.Many2one('product.product', string="Product Name" , required=True)
    quantity = fields.Float()
    available = fields.Boolean()
    state = fields.Selection([('New', 'New'),('Approved','Approved'), ('Sent', 'Sent'),('Waiting','Waiting'),('Ready','Ready'),
                              ('Received', 'Received'),('Assigned','Assigned'), ('Canceled', 'Canceled'),('Reconciled', 'Reconciled') ], track_visibility='onchange', default ='New')
    location_id = fields.Many2one('stock.location',string='Location SRC')
    location_dst_id = fields.Many2one('stock.location',string='Location DST')
    picking_type_id = fields.Many2one('stock.picking.type',)
    used_by = fields.Selection([('Employee', 'Employee'), ('Department', 'Department'), ],  default='Employee')
    employee_id = fields.Many2one("hr.employee", )
    department_id = fields.Many2one('hr.department', string='Department')
    technician = fields.Many2one('res.users',string="Requested By",default=lambda self :self.env.uid , readonly=True)
    assigned_date = fields.Date(readonly=True)
    request_date = fields.Date(readonly=True , default= date.today())
    note = fields.Text(string="Description")
    company_id = fields.Many2one('res.company',string='Company', readonly=True, copy=False,
        default=lambda self: self.env['res.company']._company_default_get(),)

    @api.model
    def create(self, vals):
        _logger.info("Create")
        sequence = self.env['ir.sequence'].next_by_code('product.custody')
        vals['name'] = sequence
        custody = super(ProductCustody, self).create(vals)
        return custody

    @api.constrains('quantity')
    def _check_quantity(self):
        _logger.info("quantity")
        if not self.available:
            raise ValidationError(_('You Cannot Create Request , Check Quantity'))
        if self.quantity <= 0:
            raise ValidationError(_('You cannot create request with  " quantity <= 0 ". '))


    @api.onchange('product_id', 'quantity')
    def product_qty(self):

        if self.product_id:
            _logger.info("product_qty")
            self.check_available_product()

    def check_available_product(self):
        _logger.info("check_available_product")

        product_quty_ob = self.env['stock.quant'].search([('location_id.usage','=', 'internal'),('product_id','=',self.product_id.id)])
        print("qty_available")
        if not self.product_id.qty_available:
            self.available = False
            
        else:
            print(self.product_id.qty_available)
            self.available = True
             
        _logger.info("AVIIIII")
        _logger.info(self.available)
        _logger.info(self.product_id.qty_available)

    def send_stock_req(self):
        _logger.info("send_stock_req")
        self.get_inventory_locations()
        print("i am in stock ")
        user_id = self.env['res.partner'].search([('name', 'ilike', self.technician.name)],limit=1)
        product_id = self.product_id
        print("before create",self.picking_type_id.id,self.location_id.id, self.location_dst_id.id)
        picking_out = self.env['stock.picking'].create({
            'partner_id': user_id.id,
            'state': 'draft',
            'origin':self.name,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dst_id.id,
            'move_lines': [],
        })
        print("after create")
        self.env['stock.move'].create({
            'name': product_id.name,
            'product_id': product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': product_id.uom_id.id,
            'picking_id': picking_out.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dst_id.id,
        })
        picking_out.action_confirm()
        self.state = "Sent"

    def get_inventory_locations(self):
        _logger.info("get_inventory_locations")
        user_company =  self.env.user.company_id.id
        print(user_company,self.env.user.company_id,self.env.user.company_id.name)
        company_partner = self.env['res.company'].search([('id','=',user_company)],limit=1)
        print(company_partner,"company_partner")
        warehouse_id = self.env['stock.warehouse'].search([('company_id','=',company_partner.id)],limit=1)
        print("wearwhouse id ", warehouse_id)
        operation_type_ids = self.env['stock.picking.type'].search([('warehouse_id','=',warehouse_id.id)],limit=1)
        operation_id = self.env['stock.picking.type']
        for op in operation_type_ids:
            print(op.id)
            print(op.name)
            if op.name == 'Delivery Orders':
                print("i am in delivery order")
                operation_id = op.id
                self.picking_type_id = operation_id
                if op.custody_stock_src_id:
                    self.location_id = op.custody_stock_src_id.id
                else:
                    raise ValidationError(_('you should add default custody Source Location'))
                if op.custody_stock_dst_id.id:
                    self.location_dst_id = op.custody_stock_dst_id.id
                else :
                    raise ValidationError(_('you should add default custody Destination Location'))

    def check_availability(self):
        _logger.info("check_availability")
        stock_req = self.env['stock.picking'].search([('origin','like',self.name)])
        print(stock_req.state)
        if stock_req.state == 'assigned' or stock_req.state == 'done' :
            self.write({'state': "Ready"})
        else:
            self.state = "Waiting"

    def Approve_custody_req(self):
        _logger.info("Approve_custody_req")

        self.state = "Approved"

    def cancel_progress(self):
        _logger.info("cancel_progress")
        self.state = "Canceled"

    def receive_product(self):
        _logger.info("receive_product")
        stock_req = self.env['stock.picking'].search([('origin', 'like', self.name)])
        print(stock_req.state)
        if stock_req.state == 'done':
            self.write({'state': "Received"})

    def assign_product_to_employee(self):
        _logger.info("assign_product_to_employee")
        self.assigned_date = date.today()
        self.state = "Assigned"

     
    def unlink(self):
        _logger.info("unlink")
        for rec in self.filtered(lambda custody: custody.state not in ['New']):
            raise UserError(_('You can not delete a custody which is in "Not New" state !!'))
        return super(ProductCustody, self).unlink()

    def reconcile_custody(self):
        _logger.info("reconcile_custody")
        print(" i am in reconcile")
        view = self.env.ref('product_custody.product_custody_reconcile_form_view')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['default_employee_id'] = self.employee_id.id
        context['default_quantity'] = self.quantity
        context['default_product_id'] = self.product_id.id
        context['default_custody_id'] = self.id
        context['default_used_by'] = self.used_by
        context['default_department_id'] = self.department_id.id
        # context['employee_id'] = self.employee_id.id
        return {
            'name': "Success",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'product.custody.reconcile',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }