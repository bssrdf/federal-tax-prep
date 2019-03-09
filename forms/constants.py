constants = {}

constants["STANDARD_DEDUCTION"] = { 
	"2018": {
		"single":            12000,
		"married_joint":     24000,
		"widower":           24000,
		"married_separate":  12000,
		"head_of_household": 18000
	}
}

# for senior citizens or blind
constants["STANDARD_DEDUCTION+"] =  {
	"2018": {
		"single":            1600,
		"married_joint":     1300,
		"widower":           1300,
		"married_separate":  1300,
		"head_of_household": 1600
	}
}

constants["DEPENDENTS_CREDIT_INCOME_THRESHOLD"] = {
	"2018": {
		"single":            200000,
		"married_joint":     400000,
		"widower":           200000,
		"married_separate":  200000,
		"head_of_household": 200000
	}
}

constants["DEPENDENTS_CREDIT_AMT"] = {
	"2018": {
		"all": { "child": 2000, "other": 500 }
	}
}

constants["QBI_THRESHOLD"] = {
	"2018": {
		"all": 157500
	}
}

constants["MAX_DEDUCTIBLE_STATE_TAX"] = {
	"2018": {
		"all": 10000
	}
}

TAX_YEAR = "2018"

def get_value(key, filing_status="single", tax_year=TAX_YEAR):
	table = constants[key][tax_year]

	if 'all' in table:
		# same value for all filing statuses
		return table['all']
	
	return table[filing_status]