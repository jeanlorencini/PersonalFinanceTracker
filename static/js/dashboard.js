// Dashboard JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard components
    initializeDashboard();
});

function initializeDashboard() {
    // Load chart data if chart exists
    const chartCanvas = document.getElementById('expensesChart');
    if (chartCanvas) {
        loadExpensesChart();
    }
    
    // Add animations to cards
    animateCards();
    
    // Set up auto-refresh for real-time data (optional)
    // setInterval(refreshDashboard, 300000); // Refresh every 5 minutes
}

function loadExpensesChart() {
    // This function is called if there's chart data available
    // The actual chart initialization is done in the template
    console.log('Expenses chart initialized');
}

function animateCards() {
    // Add entrance animations to dashboard cards
    const cards = document.querySelectorAll('.bg-white.shadow');
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.3s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function refreshDashboard() {
    // Function to refresh dashboard data without page reload
    // This would make an AJAX call to get updated data
    console.log('Refreshing dashboard data...');
    
    fetch('/api/dashboard_data')
        .then(response => response.json())
        .then(data => {
            updateChartData(data);
        })
        .catch(error => {
            console.error('Error refreshing dashboard:', error);
        });
}

function updateChartData(data) {
    // Update the chart with new data
    const chart = Chart.getChart('expensesChart');
    if (chart) {
        chart.data.labels = data.labels;
        chart.data.datasets[0].data = data.data;
        chart.update();
    }
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(amount);
}

// Add click handlers for quick actions
document.addEventListener('click', function(e) {
    // Handle quick action buttons
    if (e.target.classList.contains('quick-action')) {
        const action = e.target.dataset.action;
        handleQuickAction(action);
    }
});

function handleQuickAction(action) {
    switch(action) {
        case 'import':
            window.location.href = '/import';
            break;
        case 'transactions':
            window.location.href = '/transactions';
            break;
        default:
            console.log('Unknown action:', action);
    }
}

// Export functions for use in other files
window.dashboardUtils = {
    formatCurrency,
    refreshDashboard,
    updateChartData
};
