from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EstateProperty(models.Model):
    _inherit = "estate.property"

    sales_id = fields.Many2one('res.users', required=True)

    @api.model_create_multi
    def create(self, vals):
        for v in vals:
            sales_person_property_ids = self.env[self._name].search_count([("sales_id", "=", v.get("sales_id"))])
            if sales_person_property_ids >= 2:
                raise ValidationError("User has enough properties assigned to him already")
            
        return super(EstateProperty, self).create(vals)