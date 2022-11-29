# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class UserInherit(models.Model):

	_inherit = 'res.users'

	user_pricelist = fields.Many2many('product.pricelist',string="User Price List",store="True")

	all_pricelist = fields.Many2many('product.pricelist',string="All Price Lists",compute="compute_pricelists")

	def compute_pricelists(self):
		for rec in self:
			if len(rec.user_pricelist.ids) <= 0:
				rec.all_pricelist = [(6,0,self.env['product.pricelist'].sudo().search([]).ids )]
			else:
				rec.all_pricelist = False
