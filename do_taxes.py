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

import forms.s_1040
import forms.s1_1040
import forms.s3_1040
import forms.s4_1040
import forms.s5_1040
import forms.a_1040
import forms.b_1040
import forms.se_1040
import forms.cez_1040
import forms.sep_ira
import forms.f_8606
import forms.s_1040v
import forms.tax_worksheet
import forms.constants
import forms.utils

from PyPDF2 import PdfFileMerger
import argparse
import sys
import os

data = forms.utils.parse_values()

def main():
            
    parser = argparse.ArgumentParser(description='A Python-based tax filing solution')
    fill_forms()

    print('Your tax forms are now filled out, and available in the `filled` directory.')

def fill_forms():

    OUTPUT_DIRECTORY = "filled/%s" % forms.constants.TAX_YEAR

    # Create output directory for tax year.        
    try:  
        os.makedirs(OUTPUT_DIRECTORY)
    except OSError:
        pass

    # Attach Form-1040 first
    output_pdfs = []
    output_file, f1040_data = forms.s_1040.fill_in_form()
    output_pdfs.append(output_file)

    # Supporting forms/schedules/worksheets
    additional_forms_to_attach = [forms.s1_1040, forms.s3_1040, forms.s4_1040, forms.s5_1040, forms.tax_worksheet, forms.a_1040, forms.b_1040, forms.cez_1040, forms.se_1040]
    if '1099_r' in data:
        additional_forms_to_attach.extend([forms.f_8606, forms.sep_ira])

    # If tax is owed, attach voucher
    if "_owed" in f1040_data and f1040_data["_owed"] > 0:
        additional_forms_to_attach.append(forms.s_1040v)

    for form in additional_forms_to_attach:
        output_file = form.fill_in_form()
        output_pdfs.append(output_file)

    # Merge all forms
    merger = PdfFileMerger()
    for pdf_path in output_pdfs:
        merger.append(open(pdf_path, 'rb'))

    with open(os.path.join(OUTPUT_DIRECTORY, 'Full_Tax_Return.pdf'), 'wb') as fd:
        merger.write(fd)

if __name__ == '__main__':
    main()
