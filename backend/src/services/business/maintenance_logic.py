from datetime import date

def get_available_years(records):
    """Restituisce la lista degli anni disponibili + l'anno corrente."""
    current_year = date.today().year
    db_years = sorted(list(set(r.date.year for r in records)), reverse=True)
    if not db_years: 
        db_years = [current_year]
    return db_years

def filter_records_by_year(records, selected_option):
    """Filtra i record in base all'opzione anno (Intero o 'Tutti gli anni')."""
    if selected_option == "Tutti gli anni":
        return records, "storico"
    else:
        filtered = [r for r in records if r.date.year == selected_option]
        return filtered, str(selected_option)

def filter_records_by_category(records, selected_categories):
    """Filtra i record se ci sono categorie selezionate."""
    if not selected_categories:
        return records
    return [r for r in records if r.expense_type in selected_categories]

def get_all_categories(records):
    """Restituisce la lista unica delle categorie presenti."""
    return sorted(list(set(r.expense_type for r in records)))