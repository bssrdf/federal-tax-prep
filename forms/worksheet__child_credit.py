'''
Fills in the "Child Tax Credit and Credit for Other Dependents Worksheet"

Relies on the following forms:
    - Form 1040 (through line 11)
    - Schedule 3

Assumes you are _not_ taking:
    - Mortgage interest credit, Form 8396
    - Adoption credit, Form 8839
    - Residential energy efficient property credit, Form 5695, Part I
    - District of Columbia 1st-time homebuyer credit, Form 8859
    - Alternative vehicle credit, Form 8910
    - Electric vehicle credit, Form 8936
'''

# Instructions: https://www.irs.gov/pub/irs-pdf/p972.pdf

from . import utils
from . import constants
from . import s_1040
from . import s3_1040
import math

###################################

def qualifies_child(dependent):
    return "ssn" in dependent and "y" in dependent["age_under_17"]

def qualifies_other(dependent):
    return "ssn" not in dependent or "y" not in dependent["age_under_17"]


def build_data():

    info = utils.parse_values()

    data_dict = {}

    form_1040  = s_1040.build_data(short_circuit='Child Credit')
    schedule_3 = s3_1040.build_data()

    dependents = form_1040["dependents"]
    data_dict["dependents"] = dependents

    line_1, line_2 = 0, 0

    for dependent in dependents:
        dependent["child_credit"] = qualifies_child(dependent)
        if not dependent["child_credit"]:
            dependent["other_credit"] = qualifies_other(dependent)

        if dependent["child_credit"]:
            line_1 += constants.get_value("DEPENDENTS_CREDIT_AMT")["child"]
        elif dependent["other_credit"]:
            line_2 += constants.get_value("DEPENDENTS_CREDIT_AMT")["other"]

    line_3 = line_1 + line_2

    line_4 = utils.dollars_cents_to_float(form_1040['adjusted_gross_income_dollars'],
                                          form_1040['adjusted_gross_income_cents'])

    line_5 = 0

    line_6 = line_5 + line_4

    filing_status = info["filing_status"] if "filing_status" in info else "single"
    line_7 = constants.get_value("DEPENDENTS_CREDIT_INCOME_THRESHOLD", filing_status)

    line_8, line_9 = '', 0
    if line_6 > line_7:
        '''If the result is not a multiple of $1,000,
increase it to the next multiple of $1,000.'''
        line_8 = line_6 - line_7
        line_8 = int(math.ceil(line_8 / 1000.0) * 1000)
        line_9 = int(line_8 * 0.05)

    line_10 = 0
    if line_3 > line_9:
        line_10 = line_3 - line_9
    else:
        data_dict["_total_credits"] = 0
        return data_dict

    line_11 = utils.dollars_cents_to_float(form_1040['line_11_dollars'],
                                          form_1040['line_11_cents'])

    line_12 = utils.dollars_cents_to_float(schedule_3['nonrefundable_total_dollars'],
                                          schedule_3['nonrefundable_total_cents'])
    line_13 = line_11 - line_12

    line_14 = 0
    line_15 = line_13 - line_14
    line_16 = min(line_10, line_15)
    data_dict["_total_credits"] = line_16

    return data_dict


def fill_in_form():
    data_dict = build_data()
    basename = 'worksheet__child_credit.pdf'
    return utils.write_fillable_pdf(basename, data_dict, 'worksheet__child_credit.keys')


if __name__ == '__main__':
    fill_in_form()



