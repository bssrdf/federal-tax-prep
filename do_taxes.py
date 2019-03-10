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

from PyPDF2 import PdfFileMerger
import argparse
import sys
import os

import forms.utils
import forms.configs

import forms.s_1040
import forms.s1_1040
import forms.s3_1040
import forms.s4_1040
import forms.s5_1040
import forms.a_1040
import forms.b_1040
import forms.se_1040
import forms.cez_1040
import forms.worksheet__sep_ira
import forms.f_8606
import forms.f_8863_iii
import forms.s_1040v
import forms.worksheet__capital_gains
import forms.worksheet__child_credit

def standardize_args(args):
    args.data_basename = args.data.split("/")[-1].replace(".json", "")
    if not args.data.endswith(".json"): 
        args.data += ".json"

    if args.out is None:
        if "sample" in args.data:
            args.out = "_sample_filled/%s/%s" % (args.data_basename, args.year)
        else:
            args.out = "filled/%s" % args.year

    return args

def main():
    parser = argparse.ArgumentParser(description='A Python-based tax filing solution')
    parser.add_argument('-y', '--year', type=str, default=forms.configs.get_value("tax_year"),  help='Tax year')
    parser.add_argument('-d', '--data', type=str, default=forms.configs.get_value("data_file"), help='Path to finance data file')
    parser.add_argument('-o', '--out',  type=str, help='Output directory for filled forms')

    opts = standardize_args(parser.parse_args())
    result = fill_forms(opts)
    print('Your tax forms are now filled out, and available in the directory: `%s`' % result["out_dir"])


def fill_forms(opts):
    print(opts)

    forms.configs.register_opts(opts)

    # Create output directory for tax year.        
    try:  
        os.makedirs(opts.out)
    except OSError:
        pass

    # Attach Form-1040 first
    output_pdfs = []
    output_file, f1040_data = forms.s_1040.fill_in_form()
    output_pdfs.append(output_file)

    # Supporting forms/schedules/worksheets to attach
    additional_forms_to_attach = [forms.s1_1040, forms.s3_1040, forms.s4_1040, forms.s5_1040, forms.worksheet__capital_gains, forms.a_1040, forms.b_1040]

    data = forms.utils.parse_values()
    
    if forms.utils.has_self_employment(data):
        additional_forms_to_attach.extend([forms.cez_1040, forms.se_1040])

    if forms.utils.has_deductible_ira(data):
        additional_forms_to_attach.extend([forms.f_8606])
        if forms.utils.has_self_employment(data):
            additional_forms_to_attach.extend([forms.worksheet__sep_ira])

    for form in additional_forms_to_attach:
        output_file = form.fill_in_form()
        output_pdfs.append(output_file)

    if forms.utils.has_education(data):
        education_data = data['postsecondary_education']
        output_pdfs.append(forms.f_8863_i.fill_in_form(education_data))
        for student in education_data:
            output_pdfs.append(forms.f_8863_iii.fill_in_form(student))

    # If tax is owed, attach voucher
    if "_owed" in f1040_data and f1040_data["_owed"] > 0:
        output_pdfs.append(forms.s_1040v.fill_in_form())

    # Merge all forms
    merger = PdfFileMerger()
    for pdf_path in output_pdfs:
        merger.append(open(pdf_path, 'rb'))

    with open(os.path.join(opts.out, '%s_TaxReturn_Full.pdf' % opts.year), 'wb') as fd:
        merger.write(fd)

    result = { "out_dir": opts.out }
    return result

if __name__ == '__main__':
    main()
