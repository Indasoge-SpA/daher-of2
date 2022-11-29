# Copyright 2014 - Vauxoo http://www.vauxoo.com/
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Hr Payroll Cancel",

    'summary': """
        This module allows the user to cancel a
        payslip whatever the previous state is
        without doing a refund
    """,

    'author': "Vauxoo, Eficent, "
              "Serpent Consulting Services Pvt. Ltd.,"
              "Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/hr",
    "license": "AGPL-3",

    'category': "Human Resources",
    'version': '0.1',

    'depends': [
        "hr_payroll_account",
    ],

    'data': [
        "views/hr_payslip_view.xml",
    ],

    'demo': [
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
