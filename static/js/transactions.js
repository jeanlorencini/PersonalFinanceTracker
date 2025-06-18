// Transactions page JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeTransactions();
});

function initializeTransactions() {
    // Initialize categorization modal
    setupCategorizeModal();
    
    // Setup form validation
    setupFormValidation();
    
    // Add search functionality
    setupSearch();
    
    // Initialize tooltips or other UI components
    setupUIComponents();
}

function setupCategorizeModal() {
    // Modal functionality is handled by the functions below
    console.log('Categorization modal initialized');
}

function openCategorizeModal(transactionId, description) {
    const modal = document.getElementById('categorizeModal');
    const transactionIdInput = document.getElementById('transactionId');
    const descriptionElement = document.getElementById('transactionDescription');
    const categorySelect = document.getElementById('category_select');
    const newCategoryInput = document.getElementById('new_category');
    
    // Set transaction details
    transactionIdInput.value = transactionId;
    descriptionElement.textContent = description;
    
    // Reset form
    categorySelect.value = '';
    newCategoryInput.value = '';
    
    // Show modal
    modal.classList.remove('hidden');
    
    // Focus on category select
    categorySelect.focus();
    
    // Handle mutual exclusivity between category select and new category input
    categorySelect.addEventListener('change', function() {
        if (this.value) {
            newCategoryInput.value = '';
            newCategoryInput.disabled = true;
        } else {
            newCategoryInput.disabled = false;
        }
    });
    
    newCategoryInput.addEventListener('input', function() {
        if (this.value.trim()) {
            categorySelect.value = '';
            categorySelect.disabled = true;
        } else {
            categorySelect.disabled = false;
        }
    });
}

function closeCategorizeModal() {
    const modal = document.getElementById('categorizeModal');
    const categorySelect = document.getElementById('category_select');
    const newCategoryInput = document.getElementById('new_category');
    
    // Hide modal
    modal.classList.add('hidden');
    
    // Reset form
    categorySelect.value = '';
    newCategoryInput.value = '';
    categorySelect.disabled = false;
    newCategoryInput.disabled = false;
}

function setupFormValidation() {
    // Validate categorization form
    const categorizeForm = document.querySelector('#categorizeModal form');
    if (categorizeForm) {
        categorizeForm.addEventListener('submit', function(e) {
            const categorySelect = document.getElementById('category_select');
            const newCategoryInput = document.getElementById('new_category');
            
            if (!categorySelect.value && !newCategoryInput.value.trim()) {
                e.preventDefault();
                alert('Por favor, selecione uma categoria ou crie uma nova.');
                return false;
            }
            
            // Show loading state
            const submitBtn = e.target.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Categorizando...';
        });
    }
    
    // Validate filter form
    const filterForm = document.querySelector('form[action*="transactions"]');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            const dateFrom = document.getElementById('date_from').value;
            const dateTo = document.getElementById('date_to').value;
            
            if (dateFrom && dateTo && dateFrom > dateTo) {
                e.preventDefault();
                alert('A data inicial não pode ser maior que a data final.');
                return false;
            }
        });
    }
}

function setupSearch() {
    // Add live search functionality (optional enhancement)
    const searchInput = document.getElementById('transaction_search');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterTransactions(this.value);
            }, 300);
        });
    }
}

function filterTransactions(searchTerm) {
    const rows = document.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const description = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const visible = description.includes(term);
        row.style.display = visible ? '' : 'none';
    });
}

function setupUIComponents() {
    // Add hover effects and other UI enhancements
    const tableRows = document.querySelectorAll('tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.classList.add('bg-gray-50');
        });
        
        row.addEventListener('mouseleave', function() {
            this.classList.remove('bg-gray-50');
        });
    });
    
    // Add tooltips for truncated descriptions
    const descriptions = document.querySelectorAll('.max-w-xs.truncate');
    descriptions.forEach(desc => {
        desc.title = desc.textContent;
    });
}

// Handle modal backdrop clicks
document.addEventListener('click', function(e) {
    const modal = document.getElementById('categorizeModal');
    if (e.target === modal) {
        closeCategorizeModal();
    }
});

// Handle escape key to close modal
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('categorizeModal');
        if (!modal.classList.contains('hidden')) {
            closeCategorizeModal();
        }
    }
});

// Bulk operations (future enhancement)
function selectAllTransactions() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="transaction_ids"]');
    const selectAllCheckbox = document.getElementById('select_all');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
    
    updateBulkActionsVisibility();
}

function updateBulkActionsVisibility() {
    const checkedBoxes = document.querySelectorAll('input[type="checkbox"][name="transaction_ids"]:checked');
    const bulkActions = document.getElementById('bulk_actions');
    
    if (bulkActions) {
        bulkActions.style.display = checkedBoxes.length > 0 ? 'block' : 'none';
    }
}

// Export functions for global use
window.transactionUtils = {
    openCategorizeModal,
    closeCategorizeModal,
    filterTransactions,
    selectAllTransactions,
    updateBulkActionsVisibility
};

// Make functions globally available
window.openCategorizeModal = openCategorizeModal;
window.closeCategorizeModal = closeCategorizeModal;
