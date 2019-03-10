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
Fills in a Form 1040 Schedule 3.

The following values must be defined in data.json (in addition to any
requirements for the forms listed above):
    => name
    => ssn

In addition, you can specify any foreign tax paid by including
1099_div's and setting the 'foreign_tax' key.
'''

from . import utils
from . import f_8863_i

data = utils.parse_values()

###################################

def build_data(short_circuit=''):

    data_dict = {
      'name' : data['name'],
      'ssn'  : data['ssn']
    }

    accrued_credits = 0.0

    # Foreign tax credit
    if '1099_div' in data:
        foreign_tax_credit = 0.0
        foreign_tax_credit += sum([asset['foreign_tax'] if 'foreign_tax' in asset else 0 for asset in data['1099_div']])
        utils.add_keyed_float(foreign_tax_credit, 'foreign_tax_credit', data_dict)
        accrued_credits += foreign_tax_credit

    if short_circuit == "foreign_tax_credit":
      return accrued_credits, data_dict

    if short_circuit == "child_care":
      return accrued_credits, data_dict

    # Education credits
    if utils.has_education(data):
      education_credits = f_8863_i.build_data(data["postsecondary_education"])
      if "_nonrefundable_total" in education_credits:
        utils.add_keyed_float(education_credits["_nonrefundable_total"], 'education', data_dict)
        accrued_credits += education_credits["_nonrefundable_total"]

    if short_circuit == "education":
      return accrued_credits, data_dict

    # Sum up credits
    credit_sources = ['foreign_tax_credit',
                      'child_care',
                      'education',
                      'retirement',
                      'energy',
                      'other_credits']
    
    utils.add_keyed_float(utils.add_fields(data_dict, credit_sources), 'nonrefundable_total', data_dict)

    data_dict['_total_credits'] = utils.dollars_cents_to_float(data_dict['nonrefundable_total_dollars'], data_dict['nonrefundable_total_cents'])

    return data_dict

def fill_in_form():
    data_dict = build_data()
    data_dict['_width'] = 7
    basename = 'f1040s3.pdf'
    return utils.write_fillable_pdf(basename, data_dict, 's3.keys')


if __name__ == '__main__':
    fill_in_form()



