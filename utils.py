import pandas as pd
from datetime import datetime
import re
import logging

def process_csv_file(file):
    """
    Process uploaded CSV file and extract transaction data
    Handles semicolon delimiter and finds relevant columns
    """
    try:
        # Read CSV with semicolon delimiter
        df = pd.read_csv(file, sep=';', encoding='utf-8')
        
        # If that fails, try with different encodings
        if df.empty:
            file.seek(0)
            df = pd.read_csv(file, sep=';', encoding='latin-1')
        
        # Find columns by name (case insensitive)
        date_col = None
        description_col = None
        amount_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'data' in col_lower and not date_col:
                date_col = col
            elif 'histórico' in col_lower or 'historico' in col_lower or 'descrição' in col_lower or 'descricao' in col_lower:
                description_col = col
            elif 'valor' in col_lower or 'r$' in col_lower:
                amount_col = col
        
        if not all([date_col, description_col, amount_col]):
            logging.error(f"Required columns not found. Available: {df.columns.tolist()}")
            return None
        
        # Clean and process data
        transactions = []
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row[date_col]) or pd.isna(row[description_col]) or pd.isna(row[amount_col]):
                    continue
                
                # Parse date
                date_str = str(row[date_col]).strip()
                transaction_date = parse_date(date_str)
                if not transaction_date:
                    continue
                
                # Parse amount
                amount_str = str(row[amount_col]).strip()
                amount = parse_amount(amount_str)
                if amount is None:
                    continue
                
                # Clean description
                description = str(row[description_col]).strip()
                if not description or description.lower() in ['nan', 'none', '']:
                    continue
                
                transactions.append({
                    'date': transaction_date,
                    'description': description,
                    'amount': amount
                })
                
            except Exception as e:
                logging.error(f"Error processing row {index}: {e}")
                continue
        
        return transactions
        
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return None

def parse_date(date_str):
    """Parse date string in various formats"""
    date_formats = [
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y-%m-%d',
        '%d/%m/%y',
        '%d-%m-%y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None

def parse_amount(amount_str):
    """Parse amount string and convert to float"""
    try:
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[R$\s]', '', amount_str)
        
        # Handle different decimal separators
        if ',' in cleaned and '.' in cleaned:
            # Format like 1.234,56
            cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            # Format like 1234,56
            cleaned = cleaned.replace(',', '.')
        
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def classify_transaction_type(description):
    """
    Automatically classify transaction type based on description
    Returns: 'receita', 'despesa', or 'transferencia'
    """
    description_lower = description.lower()
    
    # Investment/Transfer patterns
    investment_patterns = [
        'aplicacao cdb', 'aplicação cdb', 'compra ações', 'compra acoes',
        'investimento', 'aplicacao', 'aplicação', 'resgate cdb',
        'resgate', 'ted investimento', 'transferencia investimento'
    ]
    
    # Income patterns
    income_patterns = [
        'salario', 'salário', 'pagamento', 'credito', 'crédito',
        'deposito', 'depósito', 'pix recebido', 'transferencia recebida'
    ]
    
    for pattern in investment_patterns:
        if pattern in description_lower:
            return 'transferencia'
    
    for pattern in income_patterns:
        if pattern in description_lower:
            return 'receita'
    
    # Default to expense if not clearly identified
    return 'despesa'
