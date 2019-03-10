#! /usr/bin/python
#    Copyright (C) 2019 pyTaxPrep
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
Fills in a Form 1040V (Payment Voucher)

Relies on a full Schedule 1040.
'''


from . import utils
from . import s_1040

###################################

def build_data(info):

    form_1040 = s_1040.build_data()

    data_dict = {
        'ssn'               : info['ssn'],
        'first_and_initial' : info['name_first'] + ' ' + info['name_middle_i'],
        'last'              : info['name_last'],
        'address'           : info['address'],
        'city_state_zip'    : '%s, %s %s' % (info['address_city'], info['address_state'], info['address_zip'])
    }
    
    if 'apartment' in info:
        data_dict['apartment'] = info['apartment']

    if '_owed' in form_1040 and form_1040['_owed'] > 0:
        utils.add_keyed_float(form_1040['_owed'], 'pay', data_dict)

    return data_dict

def fill_in_form():
    data_dict = build_data(utils.parse_values())
    basename = 'f1040v.pdf'
    return utils.write_fillable_pdf(basename, data_dict, 'f1040v.keys')


if __name__ == '__main__':
    fill_in_form()



