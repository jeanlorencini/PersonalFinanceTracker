from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Transaction, Category
from utils import process_csv_file, classify_transaction_type
from datetime import datetime, date
from sqlalchemy import and_, extract, func
from sqlalchemy.exc import IntegrityError
import os

@app.route('/')
def dashboard():
    """Dashboard with financial overview and filters"""
    # Get filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    transaction_type = request.args.get('type', 'all')
    category_id = request.args.get('category_id')
    
    # Default to current month if no filters
    if not date_from and not date_to:
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Set default date range to current month
        from datetime import date
        date_from = date(current_year, current_month, 1).isoformat()
        # Last day of current month
        if current_month == 12:
            date_to = date(current_year + 1, 1, 1) - date.resolution
        else:
            date_to = date(current_year, current_month + 1, 1) - date.resolution
        date_to = date_to.isoformat()
    
    # Build date filter
    date_filter = []
    if date_from:
        date_filter.append(Transaction.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        date_filter.append(Transaction.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    
    # Income calculation
    income_query = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == 'receita',
        *date_filter
    )
    if category_id and transaction_type in ['receita', 'all']:
        income_query = income_query.filter(Transaction.category_id == category_id)
    monthly_income = income_query.scalar() or 0
    
    # Expenses calculation
    expenses_query = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == 'despesa',
        *date_filter
    )
    if category_id and transaction_type in ['despesa', 'all']:
        expenses_query = expenses_query.filter(Transaction.category_id == category_id)
    monthly_expenses = expenses_query.scalar() or 0
    
    # Investment transfers calculation
    investments_query = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == 'transferencia',
        Transaction.amount < 0,  # Outgoing transfers (investments)
        *date_filter
    )
    monthly_investments = investments_query.scalar() or 0
    
    # Account balance (income - expenses, excluding transfers)
    account_balance = monthly_income - abs(monthly_expenses)
    
    # Expenses by category for chart
    expenses_by_category_query = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Transaction.type == 'despesa',
        *date_filter
    )
    if category_id:
        expenses_by_category_query = expenses_by_category_query.filter(Transaction.category_id == category_id)
    expenses_by_category = expenses_by_category_query.group_by(Category.name).all()
    
    # Recent transactions with filters
    transactions_query = Transaction.query.filter(*date_filter)
    if transaction_type != 'all':
        transactions_query = transactions_query.filter(Transaction.type == transaction_type)
    if category_id:
        transactions_query = transactions_query.filter(Transaction.category_id == category_id)
    
    recent_transactions = transactions_query.order_by(
        Transaction.date.desc(), 
        Transaction.created_at.desc()
    ).limit(10).all()
    
    # Get categories for manual transaction form and filters
    categories = Category.query.order_by(Category.name).all()
    
    return render_template('dashboard.html',
                         monthly_income=monthly_income,
                         monthly_expenses=abs(monthly_expenses),
                         account_balance=account_balance,
                         monthly_investments=abs(monthly_investments),
                         expenses_by_category=expenses_by_category,
                         recent_transactions=recent_transactions,
                         categories=categories,
                         filters={
                             'date_from': date_from,
                             'date_to': date_to,
                             'type': transaction_type,
                             'category_id': category_id
                         })

@app.route('/transactions')
def transactions():
    """Transactions page with filtering"""
    # Get filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    transaction_type = request.args.get('type', 'all')
    category_id = request.args.get('category_id')
    
    # Build query
    query = Transaction.query
    
    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    if transaction_type != 'all':
        query = query.filter(Transaction.type == transaction_type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    transactions_list = query.order_by(Transaction.date.desc(), Transaction.created_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    
    return render_template('transactions.html',
                         transactions=transactions_list,
                         categories=categories,
                         filters={
                             'date_from': date_from,
                             'date_to': date_to,
                             'type': transaction_type,
                             'category_id': category_id
                         })

@app.route('/import')
def import_page():
    """CSV import page"""
    return render_template('import.html')

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    """Handle CSV file upload and processing"""
    if 'csv_file' not in request.files:
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('import_page'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('import_page'))
    
    if not file.filename.lower().endswith('.csv'):
        flash('Por favor, selecione um arquivo CSV', 'error')
        return redirect(url_for('import_page'))
    
    try:
        # Process CSV file
        transactions_data = process_csv_file(file)
        
        if not transactions_data:
            flash('Não foi possível processar o arquivo CSV. Verifique o formato.', 'error')
            return redirect(url_for('import_page'))
        
        # Save transactions to database
        imported_count = 0
        duplicate_count = 0
        batch_size = 50  # Process in smaller batches
        
        for i, transaction_data in enumerate(transactions_data):
            try:
                # Classify transaction type
                transaction_type = classify_transaction_type(transaction_data['description'])
                
                transaction = Transaction(
                    date=transaction_data['date'],
                    description=transaction_data['description'],
                    amount=transaction_data['amount'],
                    type=transaction_type
                )
                
                db.session.add(transaction)
                imported_count += 1
                
                # Commit in batches
                if (i + 1) % batch_size == 0:
                    try:
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
                        # Handle duplicates in batch - reprocess individually
                        for j in range(max(0, i - batch_size + 1), i + 1):
                            try:
                                td = transactions_data[j]
                                tt = classify_transaction_type(td['description'])
                                t = Transaction(
                                    date=td['date'],
                                    description=td['description'],
                                    amount=td['amount'],
                                    type=tt
                                )
                                db.session.add(t)
                                db.session.commit()
                            except IntegrityError:
                                db.session.rollback()
                                duplicate_count += 1
                                imported_count -= 1
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(f"Error in batch commit: {e}")
                        continue
                
            except Exception as e:
                app.logger.error(f"Error processing transaction: {e}")
                continue
        
        # Commit remaining transactions
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # Process remaining individually
            remaining_start = (len(transactions_data) // batch_size) * batch_size
            for j in range(remaining_start, len(transactions_data)):
                try:
                    td = transactions_data[j]
                    tt = classify_transaction_type(td['description'])
                    t = Transaction(
                        date=td['date'],
                        description=td['description'],
                        amount=td['amount'],
                        type=tt
                    )
                    db.session.add(t)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    duplicate_count += 1
                    imported_count -= 1
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error in final commit: {e}")
        
        # Provide feedback
        if imported_count > 0:
            flash(f'Importação concluída! {imported_count} transações importadas.', 'success')
        if duplicate_count > 0:
            flash(f'{duplicate_count} transações duplicadas foram ignoradas.', 'info')
        
        return redirect(url_for('transactions'))
        
    except Exception as e:
        app.logger.error(f"CSV processing error: {e}")
        flash('Erro ao processar o arquivo CSV. Verifique o formato e tente novamente.', 'error')
        return redirect(url_for('import_page'))

@app.route('/categorize_transaction', methods=['POST'])
def categorize_transaction():
    """Categorize a transaction"""
    transaction_id = request.form.get('transaction_id')
    category_id = request.form.get('category_id')
    new_category = request.form.get('new_category')
    
    if not transaction_id:
        flash('ID da transação não fornecido', 'error')
        return redirect(url_for('transactions'))
    
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Allow categorization of expenses and income, but not transfers
    if transaction.type == 'transferencia':
        flash('Transferências não podem ser categorizadas', 'error')
        return redirect(url_for('transactions'))
    
    try:
        if new_category:
            # Create new category
            category = Category(name=new_category.strip())
            db.session.add(category)
            db.session.flush()  # Get the ID
            transaction.category_id = category.id
        elif category_id:
            transaction.category_id = int(category_id)
        
        db.session.commit()
        flash('Transação categorizada com sucesso!', 'success')
        
    except IntegrityError:
        db.session.rollback()
        flash('Categoria já existe', 'error')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Categorization error: {e}")
        flash('Erro ao categorizar transação', 'error')
    
    return redirect(url_for('transactions'))

@app.route('/add_manual_transaction', methods=['POST'])
def add_manual_transaction():
    """Add a manual transaction"""
    try:
        date_str = request.form.get('date')
        description = request.form.get('description')
        amount_str = request.form.get('amount')
        transaction_type = request.form.get('type')
        category_id = request.form.get('category_id')
        
        # Validation
        if not all([date_str, description, amount_str, transaction_type]):
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return redirect(url_for('dashboard'))
        
        # Parse date
        transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Parse amount
        amount = float(amount_str)
        
        # For expenses, make amount negative
        if transaction_type == 'despesa' and amount > 0:
            amount = -amount
        # For transfers/investments going out, make amount negative
        elif transaction_type == 'transferencia' and amount > 0:
            amount = -amount
        
        # Create transaction
        transaction = Transaction(
            date=transaction_date,
            description=description,
            amount=amount,
            type=transaction_type,
            category_id=int(category_id) if category_id else None
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transação adicionada com sucesso!', 'success')
        
    except ValueError as e:
        flash('Erro nos dados fornecidos. Verifique os valores.', 'error')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding manual transaction: {e}")
        flash('Erro ao adicionar transação.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        
        db.session.delete(transaction)
        db.session.commit()
        
        flash('Transação excluída com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting transaction: {e}")
        flash('Erro ao excluir transação.', 'error')
    
    return redirect(url_for('transactions'))

@app.route('/api/dashboard_data')
def api_dashboard_data():
    """API endpoint for dashboard chart data"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Expenses by category for chart
    expenses_by_category = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        and_(
            Transaction.type == 'despesa',
            extract('month', Transaction.date) == current_month,
            extract('year', Transaction.date) == current_year
        )
    ).group_by(Category.name).all()
    
    chart_data = {
        'labels': [item[0] for item in expenses_by_category],
        'data': [abs(float(item[1])) for item in expenses_by_category]
    }
    
    return jsonify(chart_data)
