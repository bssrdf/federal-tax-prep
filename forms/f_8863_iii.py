'''
Fills in a Form 8863 (Part III) - Student and Educational
Institution Information

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

###################################

def build_data(s_info):

    info =  utils.parse_values()

    data_dict = {
        'name': info['name'],
        'student_name': s_info['student'],
        'institution_name': s_info['institution'],
        'institution_address': s_info['address'],
        '1098_t_y': True
    }

    _constants = constants.get_value("EDUCATION_CREDIT", filing_status=info["filing_status"])

    # Populate filer's SSN
    for (i, s) in enumerate(info['ssn'].split('-')):
        data_dict['ssn_%s' % i] = s

    # Populate student's SSN
    for (i, s) in enumerate(s_info['ssn'].split('-')):
        data_dict['student_ssn_%s' % i] = s

    # Populate institution EIN
    for (i, d) in enumerate(s_info['ein'].replace('-', '')):
        data_dict['ein_%s' % i] = d

    if 'y' in s_info['is_undergrad']:
        data_dict['american_opportunity_credit_23_n'] = True
        data_dict['american_opportunity_credit_24_y'] = True
        data_dict['american_opportunity_credit_25_n'] = True
        data_dict['american_opportunity_credit_26_n'] = True
        
        line_27 = min(_constants["max_refundable_claim"], s_info["expenses"])
        data_dict['american_opportunity_credit_aqe'] = line_27
        data_dict['line_28'] = max(0, line_27 - _constants["fully_covered_refundable_expense"])
        data_dict['line_29'] = data_dict['line_28'] * _constants["partially_covered_refundable_rate"] 

        if data_dict['line_28'] == 0:
            data_dict['american_opportunity_credit_total'] = data_dict['line_27']
        else:
            data_dict['american_opportunity_credit_total'] = data_dict['line_29'] + _constants["fully_covered_refundable_expense"]

        data_dict['line_30'] = data_dict['american_opportunity_credit_total']

    else:
        data_dict['american_opportunity_credit_23_y'] = True
        # skip to line 31
        data_dict['lifetime_learning_credit_aqe'] = s_info['expenses']
        data_dict['line_31'] = data_dict['lifetime_learning_credit_aqe']

    return data_dict

def fill_in_form(student_info):
    data_dict = build_data(student_info)
    data_dict['_width'] = 9
    out_filename = 'f8863_iii__%s.pdf' % student_info["student"].replace(" ", "_").lower()
    return utils.write_fillable_pdf("f8863_iii.pdf", data_dict, 'f8863_iii.keys', output_name=out_filename)