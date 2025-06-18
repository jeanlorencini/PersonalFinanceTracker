# Finance Management Web Application

## Overview

This is a personal finance management web application built with Flask (Python) that allows users to import bank statements from CSV files and track their financial transactions. The application provides automated transaction classification, duplicate detection, and a comprehensive dashboard for financial overview.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python 3.11)
- **Database**: SQLite with SQLAlchemy ORM
- **Web Server**: Gunicorn for production deployment
- **File Processing**: Pandas for CSV parsing and data manipulation

### Frontend Architecture
- **Styling**: Tailwind CSS for responsive design
- **JavaScript**: Vanilla JavaScript for interactivity
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome for UI icons

### Database Schema
The application uses two main database models:
- **Transaction**: Stores financial transactions with fields for date, description, amount, type, category, and unique hash for duplicate detection
- **Category**: Stores transaction categories with predefined Brazilian Portuguese categories (Moradia, Alimentação, Transporte, etc.)

## Key Components

### Transaction Management
- **CSV Import**: Processes bank statement CSV files with semicolon delimiters
- **Automatic Classification**: Categorizes transactions as 'receita' (income), 'despesa' (expense), or 'transferencia' (transfer/investment)
- **Duplicate Detection**: Uses MD5 hash of date, description, and amount to prevent duplicate entries
- **Category Assignment**: Default categories in Portuguese for Brazilian users

### Dashboard
- **Monthly Overview**: Displays current month's income, expenses, and account balance
- **Investment Tracking**: Separate tracking for investment transfers
- **Expense Visualization**: Charts showing expense distribution by category
- **Recent Transactions**: List of latest financial activities

### Data Processing
- **CSV Parser**: Handles various CSV formats and encodings (UTF-8, Latin-1)
- **Column Detection**: Automatically identifies relevant columns (Data, Histórico, Valor)
- **Date Parsing**: Flexible date format handling
- **Amount Processing**: Handles Brazilian currency format

## Data Flow

1. **CSV Upload**: User uploads bank statement CSV file
2. **File Processing**: Pandas processes the CSV, identifying relevant columns
3. **Transaction Classification**: System automatically categorizes transactions based on description patterns
4. **Duplicate Check**: Hash-based duplicate detection prevents redundant entries
5. **Database Storage**: Validated transactions are stored in SQLite database
6. **Dashboard Update**: Real-time dashboard reflects new transaction data

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **Flask-SQLAlchemy**: Database ORM integration
- **Pandas**: CSV processing and data manipulation
- **Gunicorn**: WSGI HTTP server for production
- **Psycopg2-binary**: PostgreSQL adapter (for future PostgreSQL migration)
- **Email-validator**: Email validation utilities
- **Werkzeug**: WSGI utilities and middleware

### Frontend Libraries
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js**: JavaScript charting library
- **Font Awesome**: Icon library

## Deployment Strategy

### Development Environment
- Uses Flask development server with debug mode
- SQLite database for local development
- Hot reloading enabled for development workflow

### Production Environment
- **Server**: Gunicorn WSGI server
- **Binding**: 0.0.0.0:5000 with port reuse and reload capabilities
- **Scaling**: Configured for autoscale deployment target
- **Proxy**: ProxyFix middleware for proper header handling behind reverse proxies

### Database Configuration
- **Development**: SQLite database (finance.db)
- **Production**: Configurable via DATABASE_URL environment variable
- **Connection Pooling**: Enabled with 300-second recycle time and pre-ping validation

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- June 18, 2025. Initial setup