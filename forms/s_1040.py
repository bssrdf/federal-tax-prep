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
Fills in a Form 1040.

Relies on the following forms:
    - 1040 Schedule A
    - 1040 Schedule B
    - 1040 Schedule 1
    - 1040 Schedule 3
    - 1040 Schedule 4
    - 1040 Schedule 5
    
In addition, the following values must be defined in data.json:
    => name_first
    => name_middle_i
    => name_last
    => ssn
    => address
    => address_city
    => address_state
    => address_zip
    => occupation
    => w2 (list of dictionaries containing 'income' and 'federal_withheld' fields)
    => 1099_div (list of dictionaries contaiing 'total_qualified' field)
    => signature (path to an image file with your signature)

Optional keys:
    => address_apt
    => qbi_deduction

Fills in the following lines:

On page 1:
    => Your filing status, name, and SSN
    => Full year health coverage
    => Address, apartment, city, state, zip
    => Opts in to presidential election campaign
    => Occupation
    => Preparer name ("Self Prepared")
    
On page 2:
    => Line 1, 2b, 3a, 3b, 6 - 8, 10, 13 - 18, and 22

Hard coded values:
    => Opts in to contributing to the election campaign.
    => Sets the preparer name to 'Self Prepared'
    => No identity protection pin
'''

import json
import datetime
from . import utils
from . import a_1040
from . import b_1040
from . import s1_1040
from . import s3_1040
from . import s4_1040
from . import s5_1040
from . import f_8606
from . import worksheet__tax
from . import worksheet__child_credit
from . import constants

data = utils.parse_values()

###################################

# https://www.irs.gov/newsroom/tax-cuts-and-jobs-act-provision-11011-section-199a-qualified-business-income-deduction-faqs
def qualified_business_deduction(taxable_income, schedule_1, filing_status="single"):
    
    if 'qbi_deduction' not in data:
        return 0
    if data['qbi_deduction'] is not True:
        return 0

    qbi_threshold = constants.get_value("QBI_THRESHOLD", filing_status)
    if filing_status == "married_joint":
        qbi_threshold *= 2

    if taxable_income > qbi_threshold:
        raise Exception("Taxable income exceeds QBI deduction threshold -- Not Implemented!")

    # The deduction is the lesser of:

    # A) 20 percent of the taxpayer’s QBI, plus 20 percent of the
    # taxpayer’s qualified real estate investment trust (REIT)
    # dividends and qualified publicly traded partnership (PTP) income
    qbi = utils.dollars_cents_to_float(schedule_1['business_dollars'],
                                       schedule_1['business_cents'])
    option_a = qbi * 0.20

    # B) 20 percent of the taxpayer’s taxable income minus net capital
    # gains.
    capital_gains = 0
    if 'capital_gain_dollars' in schedule_1:
        capital_gains = utils.dollars_cents_to_float(schedule_1['capital_gain_dollars'],
                                                     schedule_1['capital_gain_cents'])
    option_b = 0.20 * (taxable_income - capital_gains)

    deduction = min(option_a, option_b)

    return deduction

# https://www.irs.gov/pub/irs-pdf/p501.pdf
def compute_standard_deduction(f1040_data=data, filing_status="single"):
    elderly_disabled_fields = ["senior_citizen_y", "blind_y"]
    if "married" in filing_status or "widow" in filing_status:
        elderly_disabled_fields.extend(["spouse_senior_citizen_y", "spouse_blind_y"])
    
    n = sum(map(lambda x:f1040_data[x] if x in f1040_data else False, elderly_disabled_fields))

    deduction = constants.get_value("STANDARD_DEDUCTION", filing_status) +\
    n * constants.get_value("STANDARD_DEDUCTION+", filing_status)

    return deduction

def build_data(short_circuit = ''):

    data_dict = {}

    schedule_b  = b_1040.build_data()
    schedule_1 = s1_1040.build_data()
    schedule_3 = s3_1040.build_data()
    schedule_4 = s4_1040.build_data()
    schedule_5 = s5_1040.build_data()

    filing_status = data['filing_status'] if 'filing_status' in data else "single"

    data_dict['file_%s_y' % filing_status] = True
    data_dict['first_and_initial'] = data['name_first'] + ' ' + data['name_middle_i']
    data_dict['last'] = data['name_last']
    data_dict['ssn'] = data['ssn'].replace('-', ' ')
    data_dict['home_address'] = data['address']
    if 'address_apt' in data:
        data_dict['apt_num'] = data['address_apt']
    data_dict['city_state_zip'] = '%s, %s %s' % (data['address_city'],
                                                 data['address_state'],
                                                 data['address_zip'])

    if 'blind' in data and 'y' in data['blind']:
        data_dict['blind_y'] = True
    
    if 'senior_citizen' in data and 'y' in data['senior_citizen']:
        data_dict['senior_citizen_y'] = True

    # Fill in spouse data
    if "married" in filing_status and "spouse" in data:
        data_spouse = data["spouse"]
        data_dict['spouse_first_and_initial'] = data_spouse['name_first'] + ' ' + data_spouse['name_middle_i']
        data_dict['spouse_last'] = data_spouse['name_last']
        data_dict['spouse_ssn'] = data_spouse['ssn'].replace('-', ' ')

        if 'blind' in data_spouse and 'y' in data_spouse['blind']:
            data_dict['spouse_blind_y'] = True

        if 'senior_citizen' in data_spouse and 'y' in data_spouse['senior_citizen']:
            data_dict['spouse_senior_citizen_y'] = True

    # Fill in dependents data
    if "dependents" in data:
        for n, dependent in enumerate(data["dependents"]):
            if n >= 4:
                raise Error("Too many dependents claimed!")
            data_dict['dependent_%s_name' % (n+1)] = dependent["name"]
            data_dict['dependent_%s_relationship' % (n+1)] = dependent["relationship"]
            if "ssn" in dependent:
                data_dict['dependent_%s_ssn' % (n+1)] = dependent["ssn"].replace('-', ' ')

    data_dict['health_coverage_y'] = True
    data_dict['election_campaign_y'] = True
    data_dict['occupation'] = data['occupation']
    data_dict['preparer_name'] = 'Self-Prepared'
    
    w2_income = sum([x['income'] for x in data['w2']])
    utils.add_keyed_float(w2_income, 'wages_salaries_tips', data_dict)
    
    data_dict['taxable_interest_dollars'], data_dict['taxable_interest_cents'] =\
        schedule_b['interest_total_dollars'], schedule_b['interest_total_cents']

    data_dict['ordinary_dividends_dollars'], data_dict['ordinary_dividends_cents'] =\
        schedule_b['dividend_total_dollars'], schedule_b['dividend_total_cents']

    qualified_dividends = sum([x['total_qualified'] for x in data['1099_div']])
    utils.add_keyed_float(qualified_dividends,
                          'qualified_dividends',
                          data_dict)

    distributions_total   = 0.0
    distributions_taxable = 0.0
    if '1099_r' in data:
        for x in data['1099_r']:

            # Exception 1: Rollovers from IRA -> Qualified Plan / IRA
            #              or Roth IRA -> Roth IRA
            if x['type'] == 'rollover':
                distributions_total += x['amount']
                data_dict['_rollover_flag'] = True

            if x['type'] == 'backdoor_conversion':
                distributions_total += x['converted']
                distributions_taxable += f_8606.build_data()['_taxable_amt']

        utils.add_keyed_float(distributions_total,
                              'ira_pension_annuity',
                              data_dict)
        utils.add_keyed_float(distributions_taxable,
                              'taxable_ira_pension_annuity',
                              data_dict)

    additional_income = utils.dollars_cents_to_float(schedule_1['sum_income_dollars'],
                                                     schedule_1['sum_income_cents'])

    data_dict['schedule_1_additional_income'] = str(int(round(additional_income, 0))) # '%.2f' % (additional_income)

    data_dict['_s1_income_dollars'] = schedule_1['sum_income_dollars']
    data_dict['_s1_income_cents'] = schedule_1['sum_income_cents']

    income_fields = ['wages_salaries_tips', 'ordinary_dividends', 'taxable_interest', 'taxable_ira_pension_annuity', '_s1_income']
    total_income = utils.add_fields(data_dict, income_fields)
    utils.add_keyed_float(total_income, 'total_income', data_dict)

    total_income = utils.dollars_cents_to_float(data_dict['total_income_dollars'],
                                                data_dict['total_income_cents'])
    adjustments  = utils.dollars_cents_to_float(schedule_1['adjustments_dollars'],
                                                schedule_1['adjustments_cents'])
    
    AGI = total_income - adjustments

    utils.add_keyed_float(AGI, 'adjusted_gross_income', data_dict)

    if short_circuit == 'Schedule A':
        return data_dict

    # Note: we can't calculate the Schedule A until after this point,
    # since Schedule A relies on the value for adjusted gross income.
    schedule_a = a_1040.build_data()
    itemized_deduction = utils.dollars_cents_to_float(schedule_a['total_itemized_dollars'],
                                                      schedule_a['total_itemized_cents'])

    standard_deduction = compute_standard_deduction(data_dict, filing_status)

    deduction = max(itemized_deduction, standard_deduction)
    utils.add_keyed_float(deduction, 'deductions', data_dict)
    
    taxable_income = AGI - deduction

    # This is weird ... the IRS says the QBI deduction calculation
    # involves taxable income, but taxable income depends on the
    # QBI deduction. 
    qbi_deduction = qualified_business_deduction(taxable_income, schedule_1, filing_status)
    deduction += qbi_deduction
    taxable_income -= qbi_deduction

    utils.add_keyed_float(qbi_deduction, 'qualified_business_deductions', data_dict)
    utils.add_keyed_float(taxable_income, 'taxable_income', data_dict)

    if short_circuit == 'Tax Worksheet':
        return data_dict

    worksheet = worksheet__tax.build_data()
    tax_due = worksheet['final_tax_on_income_unrounded']
    data_dict['tax_amount'] = str(int(round(tax_due, 0))) + ' '

    utils.add_keyed_float(tax_due, 'line_11', data_dict)

    # Child Credit relies on Line 11
    if short_circuit == 'Child Credit':
        data_dict["dependents"] = data["dependents"]
        return data_dict

    data_dict['schedule_3_added_y'] = True
    utils.add_keyed_float(schedule_3['_total_credits'],
                          'schedule_3',
                          data_dict)
    utils.add_keyed_float(schedule_3['_total_credits'],
                          'nonrefundable_credits',
                          data_dict)

    if "dependents" in data:
        dependent_credit_data = worksheet__child_credit.build_data()
        data_dict["dependent_tax_credit"] = str(int(round(dependent_credit_data["_total_credits"]))) + ' '
        for n, dependent in enumerate(dependent_credit_data["dependents"]):
            if dependent["child_credit"]:
                data_dict["dependent_%s_tax_credit_y" % (n+1)] = True
            elif dependent["other_credit"]:
                data_dict["dependent_%s_credit_others_n" % (n+1)] = True
        utils.add_keyed_float(dependent_credit_data["_total_credits"],
                             "dependent_tax_credit",
                             data_dict)
        utils.add_keyed_float(schedule_3['_total_credits'] + dependent_credit_data["_total_credits"],
                          'nonrefundable_credits',
                          data_dict)

    line_13 = tax_due - utils.dollars_cents_to_float(data_dict['nonrefundable_credits_dollars'],
                                                    data_dict['nonrefundable_credits_cents'])
    line_13 = max(line_13, 0)

    utils.add_keyed_float(line_13, 'line_13', data_dict)

    other_taxes = utils.dollars_cents_to_float(schedule_4['total_other_taxes_dollars'],
                                               schedule_4['total_other_taxes_cents'])

    utils.add_keyed_float(other_taxes, 'other_taxes', data_dict)

    total_tax = other_taxes + line_13

    utils.add_keyed_float(total_tax, 'total_tax', data_dict)

    federal_withheld = sum([x['federal_withheld'] for x in data['w2']])

    utils.add_keyed_float(federal_withheld, 'withheld', data_dict)

    total_credits = utils.dollars_cents_to_float(schedule_5['total_credits_dollars'],
                                                 schedule_5['total_credits_cents'])

    data_dict['refundable_schedule_5'] = str(int(round(total_credits, 0))) #'%.2f' % (total_credits)

    utils.add_keyed_float(total_credits, 'refundable', data_dict)

    payments = total_credits + federal_withheld

    utils.add_keyed_float(payments, 'total_payments', data_dict)

    if payments > total_tax:
        refund = payments - total_tax
        utils.add_keyed_float(refund, 'refund', data_dict)
        data_dict['_refund'] = refund
    else:
        owed = total_tax - payments
        utils.add_keyed_float(owed, 'owed', data_dict)
        data_dict['_owed'] = owed

    return data_dict

def fill_in_form():
    data_dict = build_data()
    data_dict['_width'] = 9
    data_dict['_signature_page'] = 1
    data_dict['_signature_x'] = 105
    data_dict['_signature_y'] = 475
    data_dict['_signature_width'] = 150
    data_dict['_signature_height'] = 20
    data_dict['_signature_path'] = data['signature']

    data_dict['_extra_annots'] = {
        1 : [ {'string' : datetime.datetime.today().strftime('%m/%d/%y'),
               'x' : 275,
               'y' : 475,
               'size' : 10} ]
        }
    basename = 'f1040.pdf'
    return utils.write_fillable_pdf(basename, data_dict, 's1040.keys'), data_dict

if __name__ == '__main__':
    fill_in_form()



