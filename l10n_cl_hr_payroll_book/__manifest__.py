# -*- coding: utf-8 -*-
{
    'name': 'Chilean Payroll Book',
    'version': '15.0.1.0.0',
    'summary': "Chilean Payroll Book",
    'description': "Chilean Payroll Book",
    'category': 'Payroll Localization',
    'author': 'Konos',
    'website': 'http://konos.cl',
    'depends': [
                'base',
                'l10n_cl',
                'l10n_cl_hr',
                ],
    'data': [
            'data/payroll_book_data.xml',
            'views/wizard_view.xml',
            'security/ir.model.access.csv',
            ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'auto_install': False,
}
