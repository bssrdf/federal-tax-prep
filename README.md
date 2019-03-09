## PyTaxPrep

A set of Python scripts to fill in common tax forms and schedules.

Modified from: https://github.com/pyTaxPrep/taxes-2018 to support more tax situations.

### Features added

+ Support for non-single filing statuses
+ Additional adjustments to income (student loan interest, health savings, traditional IRA deductions)
+ Claim credits for children/other dependents
+ [In progress] Extract U.S. tax code "magic numbers" into `forms/constants.py` file (so they are easy to modify year-to-year)
+ Use official marginal tax brackets to compute tax amount, instead of hard-coded tables
+ Modularized for multiple tax years
+ Easier to selectively attach forms by modifying main script file
+ Sensitive data files added to `.gitignore`

+ Changed sample data as new features are added

### Supported Forms

The filer has moderately-complex taxes due to:
  - A combination of W2 and 1099-MISC income.
  - A sole proprietorship (Schedule C-EZ and SE). 
  - Money in bank accounts (1099-INT) and investment accounts (1099-DIV).
  - Children or other dependents.
  - Estimated tax payments.
  - Contributions to a SEP IRA, rollovers from a SEP IRA, and/or a backdoor Roth conversion.
  - Itemized deductions (medical expenses and donations).

With that in mind, the following forms have some amount of support:
  - Form 1040 (Schedules 1, 4, 5, A, B, CEZ, and SE)
  - SEP IRA Contribution Worksheet
  - Child and Other Dependents Credit Worksheet
  - Form 8606

The filer is _not_:
  - A homeowner.

### Repository Layout

    => templates/  - Unmodified PDF forms downloaded from the IRS
    => forms/      - Python scripts for filling in various forms/schedules
    => filled/     - Directory where completed forms get placed
    => keyfiles/   - Form metadata, one for each PDF form, mapping field
                     names to readable names
    => tables/     - Marginal tax brackets for current tax year

    => data.json   - Fill in this file with finance information (see `sample_data.json` for example)
    => do_taxes.py  - Run this script to fill in all necessary forms
    => requirements.txt - For Python virtualenv, if you want to set one up


### Getting Started

    Set up your environment. Create a new virtual environment
    (`virtualenv venv`), jump into it (`source venv/bin/activate`),
    and then install required packages (`python -m pip install -r
    requirements.txt`).

    If you don't have Pip and/or Virtualenv, see
    https://pip.pypa.io/en/stable/installing/

    At this point, you should be able to generate Harry Potter's tax
    forms by running `python do_taxes.py`. The completed forms will all
    go into `filled/{tax_year}`.

    Some things to keep in mind:
      => Be careful not to commit an updated `data.json` file to a
         public repository (it is Git-ignored)

      => If you're unsure what a field is used for, try searching for
         its use in the source code. That should tell you which
         schedules rely on the field.

      => If a field doesn't apply to you, make it empty instead of
         removing it entirely. (So, strings become empty strings, 
         numbers become 0, lists become empty lists, etc..)

      => As you change `data.json`, re-generate taxes to make sure
         they still generate.


### Adding Forms

      - Add the blank PDF form to `templates/{tax_year}/` folder. 
        Download latest from IRS: https://www.irs.gov/downloads/irs-pdf
      - Add a new Python file for the form to `forms/`. Like the
        other files, it should have `fill_in_form` and `build_data`
        functions.
      - Add a keyfile for the form to `keyfiles/{tax_year}/`. Running `python
        pdf_utils/dump_file.py path/to/template.pdf` will identify field
        names; you'll need to create the readable names manually
        though.
      - If applicable, add "magic numbers" to `forms/constants.py`
      - Update `sample_data.json` with examples for any fields the form needs.
      - Update `do_taxes.py` to call into the new form.
