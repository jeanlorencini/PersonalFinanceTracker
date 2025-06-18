// Brazilian currency formatting utilities

function formatCurrencyBR(amount) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(amount);
}

function formatNumberBR(amount) {
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// Apply Brazilian currency formatting to all currency elements
function applyCurrencyFormatting() {
    // Format currency values
    document.querySelectorAll('[data-currency]').forEach(element => {
        const value = parseFloat(element.dataset.currency);
        if (!isNaN(value)) {
            element.textContent = formatCurrencyBR(value);
        }
    });
    
    // Format positive/negative indicators
    document.querySelectorAll('.text-positive, .text-negative').forEach(element => {
        const text = element.textContent.trim();
        const match = text.match(/([+-]?)R?\$?\s?([0-9,.]+)/);
        if (match) {
            const sign = match[1] || (element.classList.contains('text-positive') ? '+' : '');
            const value = parseFloat(match[2].replace(/[,.]/g, m => m === ',' ? '.' : ''));
            if (!isNaN(value)) {
                element.textContent = sign + formatCurrencyBR(Math.abs(value));
            }
        }
    });
}

// Initialize currency formatting when DOM is loaded
document.addEventListener('DOMContentLoaded', applyCurrencyFormatting);