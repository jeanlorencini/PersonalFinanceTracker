import pandas as pd
from datetime import datetime
import re
import logging

def process_csv_file(file):
    """
    Process uploaded CSV file and extract transaction data
    Handles the specific bank statement format with header information
    """
    try:
        # Read the entire file as text first to handle the specific format
        file.seek(0)
        content = file.read()
        
        # Try different encodings
        try:
            content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content = content.decode('latin-1')
            except UnicodeDecodeError:
                content = content.decode('cp1252')
        
        lines = content.strip().split('\n')
        
        # Find the header row that contains "Data Lançamento"
        header_row_index = -1
        for i, line in enumerate(lines):
            if 'Data Lançamento' in line or 'Data' in line.split(';')[0]:
                header_row_index = i
                break
        
        if header_row_index == -1:
            logging.error("Could not find transaction data header")
            return None
        
        # Extract header and data rows
        header_line = lines[header_row_index]
        data_lines = lines[header_row_index + 1:]
        
        # Parse header to identify columns
        headers = [h.strip() for h in header_line.split(';')]
        
        # Find the column indices
        date_col_idx = -1
        description_col_idx = -1
        amount_col_idx = -1
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'data' in header_lower:
                date_col_idx = i
            elif 'histórico' in header_lower or 'historico' in header_lower:
                description_col_idx = i
            elif 'valor' in header_lower:
                amount_col_idx = i
        
        if date_col_idx == -1 or description_col_idx == -1 or amount_col_idx == -1:
            logging.error(f"Required columns not found. Headers: {headers}")
            return None
        
        # Process transaction data
        transactions = []
        for line_num, line in enumerate(data_lines, start=header_row_index + 2):
            try:
                if not line.strip():
                    continue
                
                fields = line.split(';')
                
                # Skip lines that don't have enough fields
                if len(fields) < max(date_col_idx, description_col_idx, amount_col_idx) + 1:
                    continue
                
                # Extract data
                date_str = fields[date_col_idx].strip()
                description = fields[description_col_idx].strip()
                amount_str = fields[amount_col_idx].strip()
                
                # Skip empty or invalid data
                if not date_str or not description or not amount_str:
                    continue
                
                # Parse date
                transaction_date = parse_date(date_str)
                if not transaction_date:
                    logging.warning(f"Could not parse date '{date_str}' on line {line_num}")
                    continue
                
                # Parse amount
                amount = parse_amount(amount_str)
                if amount is None:
                    logging.warning(f"Could not parse amount '{amount_str}' on line {line_num}")
                    continue
                
                # Combine histórico and descrição for full description
                full_description = description
                if len(fields) > description_col_idx + 1 and fields[description_col_idx + 1].strip():
                    full_description += f" - {fields[description_col_idx + 1].strip()}"
                
                transactions.append({
                    'date': transaction_date,
                    'description': full_description,
                    'amount': amount
                })
                
            except Exception as e:
                logging.error(f"Error processing line {line_num}: {e}")
                continue
        
        logging.info(f"Successfully processed {len(transactions)} transactions")
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
    
    # Investment/Transfer patterns (based on the bank statement format)
    investment_patterns = [
        'aplicação', 'aplicacao', 'resgate', 'cdb porquinho', 'cdb',
        'compra ações', 'compra acoes', 'venda ações', 'venda acoes',
        'investimento', 'ted investimento', 'transferencia investimento',
        'credito evento b3', 'crédito evento b3', 'dividendos', 'juros s/capital'
    ]
    
    # Income patterns (based on the bank statement format)
    income_patterns = [
        'pix recebido', 'credito evento b3', 'crédito evento b3',
        'salario', 'salário', 'pagamento', 'credito', 'crédito',
        'deposito', 'depósito', 'dividendos', 'juros s/capital',
        'pix enviado devolvido', 'transferencia recebida', 'recebido'
    ]
    
    # Check for investment/transfer patterns first
    for pattern in investment_patterns:
        if pattern in description_lower:
            return 'transferencia'
    
    # Check for income patterns
    for pattern in income_patterns:
        if pattern in description_lower:
            return 'receita'
    
    # Check if it's a PIX devolvido (returned PIX) - should be income
    if 'devolvido' in description_lower and 'pix' in description_lower:
        return 'receita'
    
    # Default to expense if not clearly identified
    return 'despesa'
