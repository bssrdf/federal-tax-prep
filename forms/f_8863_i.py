'''
Fills in a Form 8863 (Part I-II) - Education Credits
(American Opportunity and Lifetime Learning Credits)

Relies on the following forms:
    - Schedule 3 (up to line 49)
    - Form 8863 Part III's for each student
    - Form 1040 (up to line 11)
    
The following values must be defined in data.json for _each_ student
listed in the "postsecondary_education" array
:
    => student (student name)
    => ssn (student's ssn)
    => institution (institution name)
    => address (institution address)
    => ein (institution's EIN from Form T-1098)
    => expenses (qualified tuition expenses only, minus all scholarships)
    => is_undergrad (whether student enrolled in first 4 years of postsecondary education?)

Additionally:
    - Each student must not have been convicted of felony drug possession or distribution.

Instructions: https://www.irs.gov/pub/irs-pdf/i8863.pdf

'''

from . import utils
from . import constants

from . import s3_1040
from . import s_1040
from . import f_8863_iii

###################################

def build_data(s_info):
    info = utils.parse_values()

    data_dict = {
        'name': info['name']
    }

    _constants = constants.get_value("EDUCATION_CREDIT", filing_status=info["filing_status"])

    f8863_iii_data = [f_8863_iii.build_data(student) for student in s_info]
    f1040_data = s_1040.build_data(short_circuit="tax_due")
    accrued_credits, _ = s3_1040.build_data(short_circuit="child_care")

    # Populate filer's SSN
    for (i, s) in enumerate(info['ssn'].split('-')):
        data_dict['ssn_%s' % i] = s

    agi = utils.dollars_cents_to_float(f1040_data["adjusted_gross_income_dollars"], f1040_data["adjusted_gross_income_cents"])
    tax_due = utils.dollars_cents_to_float(f1040_data["line_11_dollars"], f1040_data["line_11_cents"])

    ### Part I: Refundable American Opportunity Credit

    line_1 = sum([x['line_30'] if 'line_30' in x else 0 for x in f8863_iii_data])
    utils.add_keyed_float(line_1, "refundable_aggregate", data_dict)

    line_2 = _constants["refundable_income_threshold"]
    utils.add_keyed_float(line_2, "refundable_threshold", data_dict)

    line_3 = agi
    utils.add_keyed_float(line_3, "agi", data_dict)

    line_4 = line_2 - line_3
    utils.add_keyed_float(line_4, "line_4", data_dict)

    if line_4 > 0:
        line_5 = _constants["refundable_phaseout_range"]
        utils.add_keyed_float(line_5, "refundable_phaseout", data_dict)
        
        line_6 = 1.000
        if line_4 >= line_5:
            data_dict['refundable_multiplier_f1'] = '1'
            data_dict['refundable_multiplier_f2'] = '000'
        else:
            line_6 = round(1.0 * line_4 / line_5, 3)
            data_dict['refundable_multiplier_f1'] = '0'
            data_dict['refundable_multiplier_f2'] = str(int(line_6 * 1000))
        
        line_7 = round(line_6 * line_1, 2)
        utils.add_keyed_float(line_7, "refundable_subtotal", data_dict)

        line_8 = round(line_7 * _constants["refundable_rate"], 2)
        utils.add_keyed_float(line_8, "refundable_total", data_dict)

        data_dict['_refundable_credits'] = line_8
    else:
        data_dict['_refundable_credits'] = 0
        data_dict['_nonrefundable_total'] = 0
        return data_dict

    ### Part II: Nonrefundable Education Credits
    
    line_9 = line_7 - line_8
    utils.add_keyed_float(line_9, "leftover_credits", data_dict)

    line_10 = sum([x['line_31'] if 'line_31' in x else 0 for x in f8863_iii_data])
    utils.add_keyed_float(line_10, "nonrefundable_aggregate", data_dict)

    line_18 = 0
    if line_10 > 0:
        line_11 = min(line_10, _constants["max_nonrefundable_credit"])
        utils.add_keyed_float(line_11, "line_11", data_dict)

        line_12 = line_11 * _constants["nonrefundable_rate"]
        utils.add_keyed_float(line_12, "line_12", data_dict)

        line_13 = _constants["nonrefundable_income_threshold"]
        utils.add_keyed_float(line_13, "nonrefundable_threshold", data_dict)

        line_14 = agi
        utils.add_keyed_float(line_14, "agi2", data_dict)

        line_15 = line_13 - line_14
        utils.add_keyed_float(line_15, "line_15", data_dict)

        if line_15 > 0:
            line_16 = _constants["nonrefundable_phaseout_range"]
            utils.add_keyed_float(line_16, "nonrefundable_phaseout", data_dict)

            line_17 = 1.000
            if line_15 >= line_16:
                data_dict['nonrefundable_multiplier_f1'] = '1'
                data_dict['nonrefundable_multiplier_f2'] = '000'
            else:
                line_17 = round(1.0 * line_15 / line_16, 3)
                data_dict['nonrefundable_multiplier_f1'] = '0'
                data_dict['nonrefundable_multiplier_f2'] = str(int(line_17 * 1000))

            line_18 = round(line_12 * line_17, 2)

    utils.add_keyed_float(line_18, "nonrefundable_subtotal", data_dict)

    # Credit Limit Worksheet
    line_19 = min(line_18 + line_9, tax_due - accrued_credits)

    data_dict['line_19'] = line_19
    data_dict['_nonrefundable_total'] = line_19
    utils.add_keyed_float(line_19, "nonrefundable_total", data_dict)

    return data_dict


def fill_in_form(s_info):
    data_dict = build_data(s_info)
    data_dict['_width'] = 9
    return utils.write_fillable_pdf("f8863_i.pdf", data_dict, 'f8863_i.keys')