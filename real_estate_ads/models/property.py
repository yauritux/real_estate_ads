from odoo import fields, models, api, _

class Property(models.Model):
    _name = "estate.property"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # 'mail.alias.mixin'
    # 'utm.mixin', 'website.published.mixin', 'website.seo.metadata'
    _description = "Property Table"

    name = fields.Char(string="Name", required=True)
    # alias_id = fields.Many2one('mail.alias', string="Email Alias", ondelete='restrict', required=True)
    state = fields.Selection(
        [('new', 'New'), 
         ('received', 'Offer Received'), 
         ('accepted', 'Offer Accepted'), 
         ('sold', 'Sold'), 
         ('canceled', 'Canceled')],
        default='new', string="Status", group_expand='_expand_state')
    tag_ids = fields.Many2many('estate.property.tag', string="Property Tags")
    type_id = fields.Many2one('estate.property.type', string="Property Type")
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Available From")
    expected_price = fields.Monetary(string="Expected Price", tracking=True)
    best_offer = fields.Monetary(string="Best offer", compute='_compute_best_price')
    selling_price = fields.Monetary(string="Selling Price", readonly=True)
    bedrooms = fields.Integer(string="Bedrooms")
    living_area = fields.Integer(string="Living Area(sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage", default=False)
    garden = fields.Boolean(string="Garden", default=False)
    garden_area = fields.Integer(string="Garden Area")
    garden_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")], 
        string="Garden Orientation", default="north")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")
    sales_id = fields.Many2one('res.users', string="Sales Person")
    buyer_id = fields.Many2one('res.partner', string="Buyer", domain=[('is_company', '=', False)], tracking=True)
    phone = fields.Char(string="Phone", related='buyer_id.phone')
    mobile = fields.Char(string="Mobile", related='buyer_id.mobile')
    email = fields.Char(string="Email", related='buyer_id.email', tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id)

    # @api.depends('living_area', 'garden_area')
    # def _compute_total_area(self):
    @api.onchange('living_area', 'garden_area')
    def _onchange_total_area(self):
        self.total_area = self.living_area + self.garden_area
        # for rec in self:
            # rec.total_area = rec.living_area + rec.garden_area
    
    # total_area = fields.Integer(string="Total Area", compute=_compute_total_area)
    total_area = fields.Integer(string="Total Area")

    def action_sold(self):
        self.state = 'sold'

    def action_cancel(self):
        self.state = 'canceled'

    def action_send_email(self):
        mail_template = self.env.ref('real_estate_ads.offer_mail_template')
        mail_template.send_mail(self.id, force_send=True)

    def _get_emails(self):
        return ','.join(self.offer_ids.mapped('partner_email'))
    
    # @api.model
    # def create(self, vals):
    #     record = super(Property, self).create(vals)
    #     alias_values = {
    #         'alias_name': record.name,
    #         'alias_model_id': self.env['ir.model'].search([('model', '=', 'estate.property')], limit=1).id,
    #         'alias_force_thread_id': record.id,
    #         'alias_defaults': {'alias_id': record.id}
    #     }
    #     alias = self.env['mail.alias'].create(alias_values)        
    #     # alias = self.env['mail.alias'].search([('alias_full_name', '=', 'sales@bisnisin.asia')])
    #     print('alias=', alias)
    #     record.alias_id = alias.id
    #     return record
    
    # def _alias_get_creation_values(self):
    #     return {
    #         'alias_name': self.name,
    #         'alias_model_id': self.env['ir.model'].search([('model', '=', 'estate.property')], limit=1).id,
    #         'alias_force_thread_id': self.id,
    #         'alias_defaults': {'custom_model_id': self.id}
    #     }    
    
    # def _alias_get_default_thread_id(self):
    #     return self.id
    
    # def _alias_get_object_id(self, alias, mail, record):
    #     return self.id

    def message_update(self, msg_dict, update_vals=None):
        print('message_update got called...')
        print('msg_dict=', msg_dict)
        if update_vals:
            self.write(update_vals)

        return super(Property, self).message_update(msg_dict, update_vals)

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    offer_count = fields.Integer(string="Offer Count", compute=_compute_offer_count)

    # def action_property_view_offers(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': f"{self.name} - Offers",
    #         'domain': [('property_id', '=', self.id)],
    #         'view_mode': 'tree',
    #         'res_model': 'estate.property.offer'
    #     }

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for rec in self:
            if rec.offer_ids:
                rec.best_offer = max(rec.offer_ids.mapped('price'))
            else:
                rec.best_offer = 0

    def action_client_refresh(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
    
    def action_client_notify(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('You have done great so far'),
                'type': 'success', # other types: 'warning', 'danger'
                'sticky': False,
            }
        }
    
    def action_url_action(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://bisnisin.asia',
            'target': 'new' # other target: 'self (open on the same page)'
        }
    
    def _get_report_base_filename(self):
        self.ensure_one()
        return 'Estate Property - %s' % (self.name)
    
    def _compute_website_url(self):
        for rec in self:
            rec.website_url = "/properties/%s" % rec.id

    def _expand_state(self, states, domain, order):
        return [
            key for key, dummy in type(self).state.selection
        ]
    

class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "List of Property Types"

    name = fields.Char(string="Name", required=True)


class PropertyTags(models.Model):
    _name = "estate.property.tag"
    _description = "List of Property Tags"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")