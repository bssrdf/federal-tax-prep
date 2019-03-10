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
Fills in a Form 1040 Schedule 1.

Relies on the following forms:
    - Schedule C-EZ
    - Schedule SE
    - SEP IRA Worksheet

The following values must be defined in data.json (in addition to any
requirements for the forms listed above):
    => name
    => ssn

Currently, it'll fill in lines for business income and the
self-employment tax and SEP IRA contribution deductions.

'''

from . import utils
from . import constants
from . import cez_1040
from . import se_1040
from . import s_1040
from . import worksheet__sep_ira

data = utils.parse_values()

###################################

def compute_student_loan_deduction(interest_amt, agi, filing_status):
  _constants = constants.get_value("STUDENT_LOAN_DEDUCTION", filing_status)

  if interest_amt > _constants["max_deduction"]:
    interest_amt = _constants["max_deduction"]

  if agi <= _constants["phaseout_begin_threshold"]:
    return interest_amt

  if agi < _constants["phaseout_end_threshold"]:
    phaseout_range = _constants["phaseout_end_threshold"] - _constants["phaseout_begin_threshold"]
    return 1.0 * interest_amt * (agi - _constants["phaseout_begin_threshold"]) / phaseout_range

  return 0

    
def build_data(f1040_data=None):

    schedule_c, schedule_se, sep_ira = None, None, None

    if utils.has_self_employment(data):
      schedule_c  = cez_1040.build_data()
      schedule_se = se_1040.build_data()
      sep_ira = worksheet__sep_ira.build_data()
    
    if f1040_data is None:
      f1040_data = s_1040.build_data(short_circuit="total_income")
    
    data_dict = {
        'name' : data['name'],
        'ssn'  : data['ssn'],
    }

    # === Additional Income === #

    # Business income
    if schedule_c is not None:
      data_dict['business_dollars'] = schedule_c['net_profit_dollars']
      data_dict['business_cents'] = schedule_c['net_profit_cents']

    # Capital gains
    if '1099_div' in data:
        total_capital_gain = sum([x['total_capital_gain'] if 'total_capital_gain' in x else 0 for x in data['1099_div']])
        utils.add_keyed_float(total_capital_gain,
                              'capital_gain',
                               data_dict)

        data_dict['schedule_d_unneeded_y'] = True


    # Sum additional income sources
    additional_income_sources = ['refund', 'alimony', 'business', 
               'capital_gain', 'other_gains',
               'rental', 'farm', 'unemployment',
               'other_income']

    utils.add_keyed_float(utils.add_fields(data_dict, additional_income_sources),
                          'sum_income',
                          data_dict)

    # === Adjustments to Income === #

    # Educator expenses
    if 'educator_expenses' in data:
      utils.add_keyed_float(data['educator_expenses'], 'educator', data_dict)

    # Health savings deduction
    if 'health_savings_acct_deduction' in data:
      utils.add_keyed_float(data['health_savings_acct_deduction'], 'hsa', data_dict)

    # Self-employed deduction
    if schedule_se is not None:
      data_dict['self_employment_dollars'] = schedule_se['_se_deduction_dollars']
      data_dict['self_employment_cents'] = schedule_se['_se_deduction_cents']

    # SEP IRA
    if sep_ira is not None:
      data_dict['sep_dollars'], data_dict['sep_cents'] =\
          utils.float_to_dollars_cents(float(sep_ira['final_contrib_amt']))

    # Traditional IRA
    if 'traditional_ira_deduction' in data:
      utils.add_keyed_float(data['traditional_ira_deduction'], 'ira', data_dict)

    # Student loan deduction
    if 'student_loan_interest' in data and f1040_data is not None:
      if "total_income_dollars" in f1040_data:
        temp_agi = utils.dollars_cents_to_float(f1040_data["total_income_dollars"],
                                                f1040_data["total_income_cents"])
        student_loan_deduction = compute_student_loan_deduction(data["student_loan_interest"], temp_agi, data["filing_status"])
        utils.add_keyed_float(student_loan_deduction, 'loan_interest', data_dict)

    adjustments = ['educator', 'business_expenses',
                   'hsa', 'moving', 'self_employment',
                   'sep', 'se_health', 'early_penalty',
                   'alimony', 'ira', 'loan_interest']

    utils.add_keyed_float(utils.add_fields(data_dict, adjustments),
                          'adjustments',
                          data_dict)

    return data_dict

def fill_in_form(f1040_data=None):
    data_dict = build_data(f1040_data)
    data_dict['_width'] = 9
    basename = 'f1040s1.pdf'
    return utils.write_fillable_pdf(basename, data_dict, 's1.keys')

if __name__ == '__main__':
    fill_in_form()



