from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class AbstractOffer(models.AbstractModel):
    _name = "abstract.model.offer"
    _description = "Abstract Offer"

    partner_email = fields.Char(string="Email")
    phone_number = fields.Char(string="Phone Number")

    
class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _inherit = ['abstract.model.offer']
    _description = "List of Property offers"

    @api.depends('property_id', 'partner_id')
    def _compute_name(self):
        for rec in self:
            if rec.property_id and rec.partner_id:
                rec.name = f"{rec.property_id.name} - {rec.partner_id.name}"
            else:
                rec.name = False

    name = fields.Char(string="Description", compute=_compute_name)

    price = fields.Float(string="Price")
    status = fields.Selection(
        [("accepted", "Accepted"), ("rejected", "Rejected")],
        string="Status")
    partner_id = fields.Many2one("res.partner", string="Customer")
    property_id = fields.Many2one("estate.property", string="Property")
    validity = fields.Integer(string="Validity")
    deadline = fields.Date(string="Deadline", compute='_compute_deadline', inverse='_inverse_deadline')

    # @api.model
    # def _set_create_date(self):
    #     return fields.Date.today()

    # creation_date = fields.Date(string="Create Date", default=_set_create_date)
    creation_date = fields.Date(string="Create Date")

    # _sql_constraints = [
    #     ('check_validity', 'check(validity > 0)', 'Deadline cannot be set to before creation date')
    # ]

    def action_accept_offer(self):        
        if self.property_id:
            self._validate_accepted_offer()
            self.property_id.write({
                'selling_price': self.price,
                'state': 'accepted'
            })

            print('action_accept::statuses=', self.property_id.offer_ids.mapped('status'))
            print('action_accept::all_status=', all(self.property_id.offer_ids.mapped('status')))

            # self.property_id.selling_price = self.price
        
        self.status = 'accepted'

    def _validate_accepted_offer(self):
        offer_ids = self.env['estate.property.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('status', '=', 'accepted')
        ])
        if offer_ids:
            raise ValidationError("You have an accepted offer already")

    def action_decline_offer(self):
        self.status = 'rejected'
        print('action_decline::statuses=', self.property_id.offer_ids.mapped('status'))
        print('action_decline::all_status=', all(self.property_id.offer_ids.mapped('status')))
        if all(self.property_id.offer_ids.mapped('status')):
            self.property_id.write({
                'selling_price': 0,
                'state': 'received'
            })

    @api.depends('validity', 'creation_date')
    # @api.depends_context('uid')
    def _compute_deadline(self):
        # print(self.env.context)
        # print(self._context)
        for rec in self:
            if rec.creation_date and rec.validity:
                rec.deadline = rec.creation_date + timedelta(days=rec.validity)
            else:
                rec.deadline = False

    def _inverse_deadline(self):
        for rec in self:
            if rec.deadline and rec.creation_date:
                rec.validity = (rec.deadline - rec.creation_date).days
            else:
                rec.validity = False

    # @api.autovacuum
    # def _clean_offers(self):
    #     self.search([('status', '=', 'rejected')]).unlink()

    @api.model_create_multi
    def create(self, vals):
        for rec in vals:
            if not rec.get('creation_date'):
                rec['creation_date'] = fields.Date.today()
        
        return super(PropertyOffer, self).create(vals)
    
    @api.constrains('validity')
    def _check_validity(self):
        for rec in self:
            if rec.deadline and rec.creation_date and rec.deadline <= rec.creation_date:
                raise ValidationError(_("Deadline cannot be set to before creation date"))

    def extend_offer_deadline(self):
        print('context=', self._context)
        active_ids = self._context.get('active_ids', [])
        print(active_ids)
        if active_ids:
            offer_ids = self.env['estate.property.offer'].browse(active_ids)
            for offer in offer_ids:
                offer.validity = 10

    def _extend_offer_deadline(self):
        offer_ids = self.env['estate.property.offer'].search([])
        for offer in offer_ids:
            offer.validity = offer.validity + 1