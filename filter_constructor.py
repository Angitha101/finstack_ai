class FilterConstructor:
    @staticmethod
    def construct_filter_clause(matches):
        clauses = []
        column_mapping = {
            'PNL Type': 'pnl_type',
            'Category': 'category',
            'realm_id': 'realm_id',
            'Account': 'account',
            'Account Type': 'account_type',
            'Account Sub Type': 'account_sub_type',
            'Business Unit': 'business_unit',
            'Class': 'class',
            'Customer': 'customer',
            'Vendor': 'vendor'
        }

        for key, values in matches.items():
            if values:
                column = column_mapping.get(key)
                quoted_values = [f"'{v}'" for v in values]
                clauses.append(f"{column} IN ({', '.join(quoted_values)})")

        return " AND ".join(clauses) if clauses else ""
    

filer_constructor=FilterConstructor()