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

data = utils.parse_values()

###################################

def build_data(sdata):
    data_dict = {
        'name': data['name'],
        'student_name': sdata['student'],
        'institution_name': sdata['institution'],
        'institution_address': sdata['address'],
        '1098_t_y': True
    }

    _constants = constants.get_value("EDUCATION_CREDIT", filing_status=data["filing_status"])

    # Populate filer's SSN
    for (i, s) in enumerate(data['ssn'].split('-')):
        data_dict['ssn_%s' % i] = s

    # Populate student's SSN
    for (i, s) in enumerate(sdata['ssn'].split('-')):
        data_dict['student_ssn_%s' % i] = s

    # Populate institution EIN
    for (i, d) in enumerate(sdata['ein'].replace('-', '')):
        data_dict['ein_%s' % i] = d

    if 'y' in sdata['is_undergrad']:
        data_dict['american_opportunity_credit_23_n'] = True
        data_dict['american_opportunity_credit_24_y'] = True
        data_dict['american_opportunity_credit_25_n'] = True
        data_dict['american_opportunity_credit_26_n'] = True
        
        line_27 = min(_constants["max_refundable_claim"], sdata["expenses"])
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
        data_dict['lifetime_learning_credit_aqe'] = sdata['expenses']
        data_dict['line_31'] = data_dict['lifetime_learning_credit_aqe']

    return data_dict

def fill_in_form(student_data):
    data_dict = build_data(student_data)
    data_dict['_width'] = 9
    out_filename = 'f8863_iii__%s.pdf' % student_data["student"].replace(" ", "_").lower()
    return utils.write_fillable_pdf("f8863_iii.pdf", data_dict, 'f8863_iii.keys', output_name=out_filename)