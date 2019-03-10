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
Fills in a Schedule SE form.

Relies on Schedule C, plus the 'name' and 'ssn' fields from data.json.

Does not support net farm profit or social security.
'''

from . import utils
from . import constants

from . import cez_1040

data = utils.parse_values()

###################################

def build_data():

    data_dict = {
        'ez_name'             : data['name'],
        'ez_ssn'              : data['ssn'],
        'name'             : data['name'],
        'ssn'              : data['ssn']
        }


    w2_income = sum([x['ss_wages'] for x in data['w2']])

    schedule_c = cez_1040.build_data()

    se_income = utils.dollars_cents_to_float(schedule_c['net_profit_dollars'],
                                             schedule_c['net_profit_cents'])

    if se_income + w2_income > constants.get_value("SE_TAXES")["long_schedule_threshold"]:
        build_long_schedule_se(data_dict, se_income)
    else:
        build_short_schedule_se(data_dict, se_income)

    return data_dict

def build_short_schedule_se(data_dict, se_income):

    constants_se_taxes = constants.get_value("SE_TAXES")
    combined_FICA_rate = constants_se_taxes["medicare_rate"] + constants_se_taxes["social_security_rate"]

    line_2 = se_income
    line_3 = line_2
    # Taxable amount (subtract employer's share of FICA)
    line_4 = line_3 * (1 - combined_FICA_rate*0.5)
    # Tax burden
    line_5 = line_4 * combined_FICA_rate
    # Deductible tax
    line_6 = line_5 * 0.50

    utils.add_keyed_float(line_2, 'ez_line_2', data_dict)
    utils.add_keyed_float(line_3, 'ez_line_3', data_dict)
    utils.add_keyed_float(line_4, 'ez_line_4', data_dict)
    utils.add_keyed_float(line_5, 'ez_line_5', data_dict)
    utils.add_keyed_float(line_6, 'ez_line_6', data_dict)

    utils.add_keyed_float(line_6, '_se_deduction', data_dict)
    utils.add_keyed_float(line_5, '_se_tax',data_dict)


def build_long_schedule_se(data_dict, se_income):

    constants_se_taxes = constants.get_value("SE_TAXES")
    combined_FICA_rate = constants_se_taxes["medicare_rate"] + constants_se_taxes["social_security_rate"]

    line_2 = se_income
    utils.add_keyed_float(line_2, 'net_profit', data_dict)

    line_3 = line_2
    utils.add_keyed_float(line_3, 'line_3', data_dict)

    # Taxable SE income
    line_4 = line_3 * (1 - combined_FICA_rate/2) if line_3 > 0 else line_3
    utils.add_keyed_float(line_4, 'line_4a', data_dict)
    utils.add_keyed_float(line_4, 'line_4c', data_dict)

    if line_4 < constants_se_taxes["untaxed_threshold"]:
      utils.add_keyed_float(0, '_se_tax', data_dict)
      utils.add_keyed_float(0, '_se_deduction', data_dict)
      return

    line_6 = line_4
    utils.add_keyed_float(line_6, 'line_6', data_dict)

    line_8a = sum(x['ss_wages'] for x in data['w2'])
    utils.add_keyed_float(line_8a, 'total_ss_wages', data_dict)

    line_8d = line_8a
    utils.add_keyed_float(line_8d, 'line_8d', data_dict)

    line_9 = max(0, constants_se_taxes["long_schedule_threshold"] - line_8d)
    utils.add_keyed_float(line_9, 'line_9', data_dict)

    line_10 = min(line_6, line_9) * combined_FICA_rate
    utils.add_keyed_float(line_10, 'line_10', data_dict)

    # Medicare portion
    line_11 = line_6 * constants_se_taxes["medicare_rate"]
    utils.add_keyed_float(line_11, 'line_11', data_dict)

    line_12 = line_10 + line_11
    utils.add_keyed_float(line_12, 'se_tax', data_dict)
    utils.add_keyed_float(line_12, '_se_tax', data_dict)

    line_13 = line_12 * 0.5
    utils.add_keyed_float(line_13, 'se_deduction', data_dict)
    utils.add_keyed_float(line_13, '_se_deduction', data_dict)


def fill_in_form():
    data_dict = build_data()
    data_dict['_width'] = 9
    basename = 'f1040sse.pdf'
    return utils.write_fillable_pdf(basename, data_dict, 'sse.keys')


if __name__ == '__main__':
    fill_in_form()



