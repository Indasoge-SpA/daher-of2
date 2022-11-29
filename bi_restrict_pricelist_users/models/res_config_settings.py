# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class SaleSettings(models.TransientModel):

	_inherit = 'res.config.settings'

	restrict_user = fields.Boolean(string="User Pricelist Restriction")

	def remove_rules(self):
		rule_user = self.env['ir.rule'].search([['name','=','Restrict PriceList User']],limit=1)
		if rule_user:
			rule_user.active = False
		rule_all_doc = self.env['ir.rule'].search([['name','=','Restrict PriceList All Doc']],limit=1)
		if rule_all_doc:
			rule_all_doc.active = False            
		rule_manager = self.env['ir.rule'].search([['name','=','Restrict PriceList Manager']],limit=1)
		if rule_manager:
			rule_manager.active = False        
		itemrule_user = self.env['ir.rule'].search([['name','=','Restrict PriceList Item User']],limit=1)
		if itemrule_user:
			itemrule_user.active = False
		itemrule_all_doc = self.env['ir.rule'].search([['name','=','Restrict PriceList Item All Doc']],limit=1)
		if itemrule_all_doc:
			itemrule_all_doc.active = False            
		itemrule_manager = self.env['ir.rule'].search([['name','=','Restrict PriceList Item Manager']],limit=1)
		if itemrule_manager:
			itemrule_manager.active=False            


	def manage_rules(self):
		self.remove_rules()

		if self.restrict_user:
			rule_user = self.env['ir.rule'].search([['name','=','Restrict PriceList User']],limit=1)
			if rule_user:
				rule_user.active = True
			rule_all_doc = self.env['ir.rule'].search([['name','=','Restrict PriceList All Doc']],limit=1)
			if rule_all_doc:
				rule_all_doc.active =True
			rule_manager = self.env['ir.rule'].search([['name','=','Restrict PriceList Manager']],limit=1)
			if rule_manager:
				rule_manager.active =True	            	
			itemrule_user = self.env['ir.rule'].search([['name','=','Restrict PriceList Item User']],limit=1)
			if itemrule_user:
				itemrule_user.active = True
			itemrule_all_doc = self.env['ir.rule'].search([['name','=','Restrict PriceList Item All Doc']],limit=1)
			if itemrule_all_doc:
				itemrule_all_doc.active = True
			itemrule_manager = self.env['ir.rule'].search([['name','=','Restrict PriceList Item Manager']],limit=1)
			if itemrule_manager:
				itemrule_manager.active =True

	def set_values(self):
		super(SaleSettings, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('bi_restrict_pricelist.restrict_user', self.restrict_user)
		self.manage_rules()

	@api.model
	def get_values(self):
		res = super(SaleSettings, self).get_values()
		res.update({
			'restrict_user':bool(self.env['ir.config_parameter'].sudo().get_param('bi_restrict_pricelist.restrict_user')),
			})
		return res
