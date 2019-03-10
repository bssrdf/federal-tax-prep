from . import configs

constants = dict()

constants["STANDARD_DEDUCTION"] = { 
	"2018": {
		"single,married_separate": 12000,
		"married_joint,widowed":   24000,
		"head_of_household":       18000
	}
}

# for senior citizens or blind
constants["STANDARD_DEDUCTION+"] =  {
	"2018": {
		"single,head_of_household":               1600,
		"married_joint,widowed,married_separate": 1300,
	}
}

constants["CAPITAL_GAINS_BRACKETS"] = {
	"2018": {
		"single":                [{"threshold": 38600, "tax_rate": 0.15}, {"threshold": 425800, "tax_rate": 0.20}],
		"married_joint,widowed": [{"threshold": 77200, "tax_rate": 0.15}, {"threshold": 479000, "tax_rate": 0.20}],
		"head_of_household":     [{"threshold": 51700, "tax_rate": 0.15}, {"threshold": 452400, "tax_rate": 0.20}],
		"married_separate":      [{"threshold": 38600, "tax_rate": 0.15}, {"threshold": 239500, "tax_rate": 0.20}]
	}
}

constants["SE_TAXES"] = {
	"2018": {
		"all": {
			"untaxed_threshold": 400,
			"social_security_rate": 0.124,
			"medicare_rate":        0.029,
			"long_schedule_threshold": 128400
		}
	}
}

# as percentage of adjusted gross income
constants["NONDEDUCTIBLE_MEDICAL_EXPENSE_RATE"] = {
	"2018": {
		"all": 0.075 
	},
	"2019": {
		"all": 0.100
	}
}

constants["STUDENT_LOAN_DEDUCTION"] = {
	"2018": {
		"single,married_separate,widowed,head_of_household": {
			"phaseout_begin_threshold": 65000,
			"phaseout_end_threshold":   80000,
			"max_deduction": 2500
		},
		"married_joint": {
			"phaseout_begin_threshold": 135000,
			"phaseout_end_threshold":   165000,
			"max_deduction": 2500
		}
	}
}

constants["DEPENDENTS_CREDIT_INCOME_THRESHOLD"] = {
	"2018": {
		"single,widowed,married_separate,head_of_household": 200000,
		"married_joint": 400000
	}
}

constants["DEPENDENTS_CREDIT_AMT"] = {
	"2018": {
		"all": { "child": 2000, "other": 500 }
	}
}

constants["EDUCATION_CREDIT"] = {
	"2018": {
		"single,widowed,married_separate,head_of_household": {
			"refundable_income_threshold": 90000,
			"refundable_phaseout_range":   10000,
			"refundable_rate": 0.4,
			"max_refundable_expense": 4000,
			"fully_covered_refundable_expense": 2000,
			"partially_covered_refundable_rate": 0.25,
			"max_nonrefundable_credit": 10000,
			"nonrefundable_rate": 0.2,
			"nonrefundable_income_threshold": 67000,
			"nonrefundable_phaseout_range":   10000
		},
		"married_joint": {
			"refundable_income_threshold": 180000,
			"refundable_phaseout_range":    20000,
			"refundable_rate": 0.4,
			"max_refundable_claim": 4000,
			"fully_covered_refundable_expense": 2000,
			"partially_covered_refundable_rate": 0.25,
			"max_nonrefundable_credit": 10000,
			"nonrefundable_rate": 0.2,
			"nonrefundable_income_threshold": 134000,
			"nonrefundable_phaseout_range" :   20000
		}
	}
}

constants["QBI_THRESHOLD"] = {
	"2018": {
		"single,widowed,married_separate,head_of_household": 157500,
		"married_joint": 315000
	}
}

constants["MAX_DEDUCTIBLE_STATE_TAX"] = {
	"2018": {
		"single,widowed,married_joint,head_of_household": 10000,
		"married_separate": 5000
	}
}

def get_value(key, filing_status="single"):
	tax_year = configs.get_value("tax_year")
	table = constants[key][tax_year]

	for key in table.keys():
		if filing_status in key:
			return table[key]

	if 'all' in table:
		# same value for all filing statuses
		return table['all']
	
	return table[filing_status]