# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "PriceList Restriction for Users",
    "version" : "15.0.0.0",
    "category" : "Sales",
    'summary': 'Restrict Pricelist for Users Restrict Pricelist for Partners Restrict Pricelist for Customer PriceList Restriction for Partner PriceList Restriction for customer pricelist access rights pricelist access for users Restrict Price-list for User Restrict price',
    "description": """ 

        PriceList Restriction for User in odoo,
        Restrict PriceList Access for User in odoo,
        User Pricelist Restriction in odoo,
        Restrict PriceList for User in odoo,
        User Price List in odoo,
        Access only allowed pricelist in odoo,

    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    "price": 15,
    "currency": 'EUR',
    "depends" : ['base','sale_management'],
    "data": [
        'security/pricelist_security.xml',
        'views/res_config_settings.xml',
        'views/res_users_view.xml',
    ],
    "license":'OPL-1',
    'qweb': [
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/Vw7rXED6QRg',
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
