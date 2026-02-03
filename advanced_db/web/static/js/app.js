// web/static/js/app.js - POPRAVLJENA VERZIJA
document.addEventListener('DOMContentLoaded', function() {
    // Global variables
    let currentPage = 1;
    let itemsPerPage = 25;
    let allBooks = [];
    let filteredBooks = [];
    let ratingChart = null;
    let priceChart = null;
    
    // DOM Elements
    const scrapeForm = document.getElementById('scrape-form');
    const exportBtn = document.getElementById('export-btn');
    const refreshBtn = document.getElementById('refresh-btn');
    const searchBox = document.getElementById('search-box');
    const ratingFilter = document.getElementById('rating-filter');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const itemsPerPageSelect = document.getElementById('items-per-page');
    const booksTableBody = document.getElementById('books-table-body');
    const scrapeStatus = document.getElementById('scrape-status');
    const bookModal = document.getElementById('book-modal');
    const closeModal = document.querySelector('.close-modal');
    
    // Stats elements
    const totalBooksEl = document.getElementById('total-books');
    const avgPriceEl = document.getElementById('avg-price');
    const avgRatingEl = document.getElementById('avg-rating');
    const lastUpdateEl = document.getElementById('last-update');
    
    // Initialize the dashboard
    initDashboard();
    
    async function initDashboard() {
        showLoading();
        await loadStats();
        await loadBooks();
        initCharts();
        setupEventListeners();
        hideLoading();
    }
    
    function showLoading() {
        booksTableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Loading books...</p>
                    </div>
                </td>
            </tr>
        `;
    }
    
    function hideLoading() {
        // Loading will be replaced when books are loaded
    }
    
    async function loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.error) {
                console.warn('No books in database yet');
                updateStatsUI(0, 0, 0);
                return;
            }
            
            if (data.success) {
                // Update stats cards
                updateStatsUI(
                    data.total_books || 0,
                    data.average_price || 0,
                    data.average_rating || 0
                );
                
                // Update charts data
                updateCharts(data);
            }
            
        } catch (error) {
            console.error('Error loading stats:', error);
            updateStatsUI(0, 0, 0);
        }
    }
    
    function updateStatsUI(total, avgPrice, avgRating) {
        totalBooksEl.textContent = total.toLocaleString();
        avgPriceEl.textContent = `£${avgPrice.toFixed(2)}`;
        avgRatingEl.textContent = avgRating.toFixed(1);
        lastUpdateEl.textContent = 'Just now';
    }
    
    async function loadBooks() {
        try {
            const response = await fetch(`/api/books?limit=1000&offset=0`);
            const data = await response.json();
            
            if (data.success) {
                allBooks = data.books || [];
                filteredBooks = [...allBooks];
                
                updateBooksTable();
                updatePagination();
            } else {
                showMessage('Error loading books: ' + (data.error || 'Unknown error'), 'error');
            }
            
        } catch (error) {
            console.error('Error loading books:', error);
            booksTableBody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; color: #f72585; padding: 40px;">
                        <i class="fas fa-exclamation-triangle"></i> Error loading books: ${error.message}
                    </td>
                </tr>
            `;
        }
    }
    
    function updateBooksTable() {
        // Apply filters
        let booksToShow = [...filteredBooks];
        
        // Apply search filter
        const searchTerm = searchBox.value.toLowerCase();
        if (searchTerm) {
            booksToShow = booksToShow.filter(book => 
                (book.title || '').toLowerCase().includes(searchTerm)
            );
        }
        
        // Apply rating filter
        const ratingValue = ratingFilter.value;
        if (ratingValue) {
            booksToShow = booksToShow.filter(book => 
                Number(book.rating) == ratingValue
            );
        }
        
        // Calculate pagination
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const pageBooks = booksToShow.slice(startIndex, endIndex);
        
        // Clear table
        booksTableBody.innerHTML = '';
        
        // Populate table
        if (pageBooks.length === 0) {
            booksTableBody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 40px;">
                        <i class="fas fa-book"></i> No books found
                    </td>
                </tr>
            `;
            return;
        }
        
        pageBooks.forEach(book => {
            const row = document.createElement('tr');
            
            // Create rating stars
            const stars = createStars(book.rating);
            
            // Determine availability class
            const availability = book.availability || '';
            const inStock = availability.toLowerCase().includes('in stock');
            
            row.innerHTML = `
                <td>
                    <strong>${book.title || 'N/A'}</strong>
                </td>
                <td class="price">£${book.price ? parseFloat(book.price).toFixed(2) : '0.00'}</td>
                <td class="rating-stars">${stars}</td>
                <td class="${inStock ? 'in-stock' : 'out-of-stock'}">
                    ${availability || 'Unknown'}
                </td>
                <td>
                    <button class="action-btn view-btn" data-id="${book.id}">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            `;
            
            booksTableBody.appendChild(row);
        });
        
        // Add event listeners to view buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const bookId = this.getAttribute('data-id');
                showBookDetails(bookId);
            });
        });
    }
    
    function createStars(rating) {
        let stars = '';
        const numericRating = Number(rating) || 0;
        for (let i = 1; i <= 5; i++) {
            if (i <= numericRating) {
                stars += '<i class="fas fa-star"></i>';
            } else {
                stars += '<i class="far fa-star empty"></i>';
            }
        }
        return stars;
    }
    
    function updatePagination() {
        const totalBooks = filteredBooks.length;
        const totalPages = Math.ceil(totalBooks / itemsPerPage);
        
        // Update page info
        document.getElementById('page-info').textContent = 
            `Page ${currentPage} of ${totalPages}`;
        
        // Update button states
        prevPageBtn.disabled = currentPage === 1;
        nextPageBtn.disabled = currentPage === totalPages || totalPages === 0;
        
        // Show/hide pagination if only one page
        if (totalPages <= 1) {
            document.querySelector('.pagination').style.display = 'none';
        } else {
            document.querySelector('.pagination').style.display = 'flex';
        }
    }
    
    function initCharts() {
        const ratingCtx = document.getElementById('ratingChart');
        const priceCtx = document.getElementById('priceChart');
        
        if (!ratingCtx || !priceCtx) {
            console.warn('Chart canvases not found');
            return;
        }
        
        ratingChart = new Chart(ratingCtx.getContext('2d'), {
            type: 'pie',
            data: {
                labels: ['★', '★★', '★★★', '★★★★', '★★★★★'],
                datasets: [{
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: [
                        '#f72585',
                        '#f8961e',
                        '#ffc107',
                        '#4cc9f0',
                        '#4361ee'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#333',
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.raw} books`;
                            }
                        }
                    }
                }
            }
        });
        
        priceChart = new Chart(priceCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['£0-5', '£5-10', '£10-15', '£15-20', '£20+'],
                datasets: [{
                    label: 'Number of Books',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: '#4361ee',
                    borderColor: '#3a0ca3',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Books',
                            color: '#333'
                        },
                        ticks: {
                            color: '#666'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Price Range (£)',
                            color: '#333'
                        },
                        ticks: {
                            color: '#666'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    function updateCharts(stats) {
        if (!ratingChart || !priceChart) return;
        
        // Update rating chart
        if (stats.books_by_rating) {
            ratingChart.data.datasets[0].data = [
                stats.books_by_rating['1_star'] || 0,
                stats.books_by_rating['2_star'] || 0,
                stats.books_by_rating['3_star'] || 0,
                stats.books_by_rating['4_star'] || 0,
                stats.books_by_rating['5_star'] || 0
            ];
            ratingChart.update();
        } else if (stats.books_by_rating) {
            // Fallback for old format
            ratingChart.data.datasets[0].data = [
                stats.books_by_rating[1] || 0,
                stats.books_by_rating[2] || 0,
                stats.books_by_rating[3] || 0,
                stats.books_by_rating[4] || 0,
                stats.books_by_rating[5] || 0
            ];
            ratingChart.update();
        }
        
        // Update price chart
        if (stats.price_distribution) {
            priceChart.data.datasets[0].data = [
                stats.price_distribution["0-5"] || 0,
                stats.price_distribution["5-10"] || 0,
                stats.price_distribution["10-15"] || 0,
                stats.price_distribution["15-20"] || 0,
                stats.price_distribution["20+"] || 0
            ];
            priceChart.update();
        }
    }
    
    function setupEventListeners() {
        // Scrape form submission
        scrapeForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const url = document.getElementById('url').value;
            const pages = parseInt(document.getElementById('pages').value);
            
            // Disable form and show loading
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
            submitBtn.disabled = true;
            
            showMessage('Scraping in progress...', 'info');
            
            try {
                const formData = new FormData();
                formData.append('url', url);
                formData.append('pages', pages);
                
                const response = await fetch('/api/scrape', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage(`Successfully scraped ${result.count} books!`, 'success');
                    
                    // Refresh data after a short delay
                    setTimeout(() => {
                        loadStats();
                        loadBooks();
                    }, 1500);
                    
                } else {
                    showMessage(result.message, 'error');
                }
                
            } catch (error) {
                showMessage('Error scraping books: ' + error.message, 'error');
            } finally {
                // Re-enable form
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
        
        // Export button
        exportBtn.addEventListener('click', async function() {
            try {
                showMessage('Exporting CSV...', 'info');
                const response = await fetch('/api/export/csv');
                const result = await response.json();
                
                if (result.success) {
                    showMessage('CSV exported successfully!', 'success');
                    
                    // Create download link
                    const link = document.createElement('a');
                    link.href = result.file;
                    link.download = 'books_export.csv';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                } else {
                    showMessage(result.message, 'error');
                }
                
            } catch (error) {
                showMessage('Error exporting: ' + error.message, 'error');
            }
        });
        
        // Refresh button
        refreshBtn.addEventListener('click', function() {
            loadStats();
            loadBooks();
            showMessage('Data refreshed!', 'success');
        });
        
        // Search box
        searchBox.addEventListener('input', function() {
            currentPage = 1;
            updateBooksTable();
            updatePagination();
        });
        
        // Rating filter
        ratingFilter.addEventListener('change', function() {
            currentPage = 1;
            updateBooksTable();
            updatePagination();
        });
        
        // Pagination
        prevPageBtn.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                updateBooksTable();
                updatePagination();
            }
        });
        
        nextPageBtn.addEventListener('click', function() {
            const totalPages = Math.ceil(filteredBooks.length / itemsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                updateBooksTable();
                updatePagination();
            }
        });
        
        // Items per page
        itemsPerPageSelect.addEventListener('change', function() {
            itemsPerPage = parseInt(this.value);
            currentPage = 1;
            updateBooksTable();
            updatePagination();
        });
        
        // Modal close
        closeModal.addEventListener('click', function() {
            bookModal.style.display = 'none';
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', function(e) {
            if (e.target === bookModal) {
                bookModal.style.display = 'none';
            }
        });
    }
    
    async function showBookDetails(bookId) {
        try {
            // Find book in allBooks
            const book = allBooks.find(b => b.id == bookId);
            
            if (!book) {
                showMessage('Book not found', 'error');
                return;
            }
            
            const modalTitle = document.getElementById('modal-title');
            const modalBody = document.getElementById('modal-body');
            
            modalTitle.textContent = book.title || 'Book Details';
            
            const ratingStars = createStars(book.rating);
            const price = book.price ? parseFloat(book.price).toFixed(2) : '0.00';
            const availability = book.availability || 'Unknown';
            const inStock = availability.toLowerCase().includes('in stock');
            
            modalBody.innerHTML = `
                <div class="book-details">
                    <div class="detail-row">
                        <strong>Title:</strong> ${book.title || 'N/A'}
                    </div>
                    <div class="detail-row">
                        <strong>Price:</strong> <span class="price">£${price}</span>
                    </div>
                    <div class="detail-row">
                        <strong>Rating:</strong> <span class="rating-stars">${ratingStars} (${book.rating || 0}/5)</span>
                    </div>
                    <div class="detail-row">
                        <strong>Availability:</strong> 
                        <span class="${inStock ? 'in-stock' : 'out-of-stock'}">${availability}</span>
                    </div>
                    <div class="detail-row">
                        <strong>Scraped At:</strong> ${book.timestamp ? new Date(book.timestamp).toLocaleString() : 'Unknown'}
                    </div>
                    <div class="detail-row">
                        <strong>ID:</strong> ${book.id || 'N/A'}
                    </div>
                </div>
                
                <div class="modal-actions" style="margin-top: 20px;">
                    <button class="btn btn-primary" onclick="window.open('${book.url || 'https://books.toscrape.com'}', '_blank')" ${!book.url ? 'disabled' : ''}>
                        <i class="fas fa-external-link-alt"></i> View on Website
                    </button>
                </div>
            `;
            
            bookModal.style.display = 'flex';
            
        } catch (error) {
            console.error('Error showing book details:', error);
            showMessage('Error showing book details', 'error');
        }
    }
    
    function showMessage(message, type) {
        scrapeStatus.textContent = message;
        scrapeStatus.className = 'status-message ' + type;
        scrapeStatus.style.display = 'block';
        
        // Auto-hide after 5 seconds (except errors)
        if (type !== 'error') {
            setTimeout(() => {
                scrapeStatus.style.display = 'none';
            }, 5000);
        }
    }
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadStats();
    }, 30000);
});
