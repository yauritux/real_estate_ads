from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
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

        self.status = 'accepted'

    def action_decline_offer(self):
        self.status = 'rejected'
        print(all(self.property_id.offer_ids.mapped('status')))
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