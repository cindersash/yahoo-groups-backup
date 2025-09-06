PREFIXES_TO_STRIP = {"re:", "fwd:", "[LETTERBOXINGTEXAS]"}

# CSS styles for the static website
CSS_STYLES = """
/* Basic styling for the archive */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f5f8fa;
}

/* Thread and message styles */
.thread-title {
    color: #24292e;
    margin-bottom: 8px;
}

.thread-meta {
    color: #6a737d;
    font-size: 0.9em;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e1e4e8;
}

.thread-messages {
    background-color: #fff;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    overflow: hidden;
}

.message {
    padding: 20px;
    border-bottom: 1px solid #eaecef;
    transition: background-color 0.2s;
}

.message:last-child {
    border-bottom: none;
}

.message:hover {
    background-color: #f6f8fa;
}

.message.first-message {
    background-color: #f8f9fa;
    border-left: 3px solid #0366d6;
}

.message.reply-message {
    margin-left: 30px;
    border-left: 2px solid #e1e4e8;
    position: relative;
}

.message.reply-message:before {
    content: '';
    position: absolute;
    left: -20px;
    top: 30px;
    width: 16px;
    height: 2px;
    background-color: #e1e4e8;
}

.message-header {
    margin-bottom: 12px;
    position: relative;
}

.message-header:after {
    content: '';
    display: table;
    clear: both;
}

.message-subject {
    font-size: 1.1em;
    font-weight: 600;
    margin: 0 0 4px 0;
    color: #24292e;
}

.reply-message .message-subject {
    color: #6a737d;
    font-size: 1em;
}

.message-meta {
    color: #6a737d;
    font-size: 0.85em;
    line-height: 1.5;
}

.message-meta strong {
    color: #24292e;
}

.message-content {
    line-height: 1.6;
}

.message-content img {
    max-width: 100%;
    height: auto;
}

.plaintext-content {
    white-space: pre-wrap;
    font-family: monospace;
}

a {
    color: #0366d6;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Pagination */
.pagination {
    margin: 40px 0 20px;
    text-align: center;
}

.pagination-controls {
    display: inline-flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 4px;
    margin: 0 auto;
    max-width: 100%;
}

.pagination a, 
.pagination span {
    padding: 8px 12px;
    margin: 0 2px;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    display: inline-block;
    min-width: 38px;
    text-align: center;
    transition: all 0.2s ease;
    color: #0366d6;
    background-color: #fff;
}

.pagination a:hover {
    background-color: #f6f8fa;
    text-decoration: none;
    border-color: #d1d5da;
}

.pagination .current {
    background-color: #0366d6;
    color: #fff;
    border-color: #0366d6;
    font-weight: 600;
}

.pagination .disabled {
    color: #d1d5da;
    cursor: not-allowed;
    background-color: #f6f8fa;
}

.pagination .ellipsis {
    border: none;
    padding: 8px 4px;
    color: #6a737d;
    background: transparent;
}

@media (max-width: 768px) {
    .pagination a, 
    .pagination span {
        padding: 6px 10px;
        min-width: 34px;
        font-size: 0.9em;
    }
    
    .pagination .ellipsis {
        padding: 6px 2px;
    }
}

/* Search */
.search-container {
    margin: 20px 0;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
    padding: 0 15px;
}

.search-form {
    display: flex;
    max-width: 600px;
    margin: 0 auto 30px;
    gap: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    overflow: hidden;
}

#search-input, #search-query {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid #e1e4e8;
    border-radius: 6px 0 0 6px;
    font-size: 16px;
    outline: none;
    transition: border-color 0.2s;
}

#search-input:focus, #search-query:focus {
    border-color: #0366d6;
    box-shadow: 0 0 0 3px rgba(3, 102, 214, 0.1);
}

#search-button, #search-form button[type="submit"] {
    padding: 12px 24px;
    background-color: #2ea44f;
    color: white;
    border: none;
    border-radius: 0 6px 6px 0;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
}

#search-button:hover, #search-form button[type="submit"]:hover {
    background-color: #2c974b;
}

#search-button:active, #search-form button[type="submit"]:active {
    background-color: #298e46;
}

/* Search results */
.search-results {
    margin-top: 20px;
}

.search-result {
    background: #fff;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    padding: 20px;
    margin-bottom: 16px;
    transition: transform 0.2s, box-shadow 0.2s;
}

.search-result:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.search-result h3 {
    margin: 0 0 8px 0;
    font-size: 18px;
}

.search-result h3 a {
    color: #0366d6;
    text-decoration: none;
}

.search-result h3 a:hover {
    text-decoration: underline;
}

.search-meta {
    color: #6a737d;
    font-size: 14px;
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.thread-dates {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 4px;
    font-size: 13px;
}

.thread-dates span {
    display: inline-flex;
    align-items: center;
    color: #6a737d;
}

.thread-dates span::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: #d1d5da;
    margin-right: 8px;
}

.thread-dates span:first-child::before {
    display: none;
}

.thread-dates span:not(:first-child) {
    padding-left: 8px;
    border-left: 1px solid #e1e4e8;
}

/* Loading indicator */
#loading {
    color: #6a737d;
    font-style: italic;
    margin: 20px 0;
}

/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    margin: 30px 0;
    flex-wrap: wrap;
}

.pagination a, .pagination span {
    padding: 8px 12px;
    margin: 0 4px;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    color: #0366d6;
    text-decoration: none;
    transition: all 0.2s;
}

.pagination a:hover {
    background-color: #f6f8fa;
    border-color: #d1d5da;
}

.pagination .current {
    background-color: #0366d6;
    color: white;
    border-color: #0366d6;
    font-weight: 600;
}

.pagination .ellipsis {
    border: none;
    padding: 8px 4px;
}

/* Responsive adjustments */
@media (max-width: 640px) {
    .search-form {
        flex-direction: column;
        gap: 10px;
    }
    
    #search-input, #search-query, #search-button, #search-form button[type="submit"] {
        width: 100%;
        border-radius: 6px;
    }
    
    .pagination {
        gap: 4px;
    }
    
    .pagination a, .pagination span {
        padding: 6px 10px;
        margin: 2px;
    }
}


/* Thread preview in index */
.thread-preview {
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 16px;
    background-color: #fff;
    transition: transform 0.2s, box-shadow 0.2s;
}

.thread-preview:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}

.thread-preview h3 {
    margin-top: 0;
    margin-bottom: 8px;
}

.thread-preview .thread-meta {
    color: #6a737d;
    font-size: 0.85em;
    margin-bottom: 8px;
}

.thread-preview .message-snippet {
    color: #586069;
    font-size: 0.95em;
    line-height: 1.5;
}

/* Responsive design */
@media (max-width: 768px) {
    body {
        padding: 10px;
    }
    
    .message {
        padding: 12px;
    }
    
    .reply-message {
        margin-left: 15px !important;
    }
}
"""

# JavaScript for client-side functionality
JAVASCRIPT_CODE = """
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (searchInput && searchResults) {
        let searchData = [];
        
        // Load search index
        fetch('search/search_index.json')
            .then(response => response.json())
            .then(data => {
                searchData = data;
                searchInput.disabled = false;
                searchInput.placeholder = 'Search threads by title or author...';
            })
            .catch(error => {
                console.error('Error loading search index:', error);
                searchInput.placeholder = 'Search not available';
            });
        
            function performSearch() {
            const query = searchInput.value.trim().toLowerCase();
            if (query.length < 2) {
                searchResults.innerHTML = '<p>Please enter at least 2 characters to search.</p>';
                searchResults.style.display = 'block';
                return;
            }
            
            // Search in threads
            const threadResults = searchData.filter(thread => {
                // Check if query matches title
                if (thread.title && thread.title.toLowerCase().includes(query)) {
                    return true;
                }
                
                // Check if query matches any author
                if (thread.authors && thread.authors.some(author => 
                    author && author.toLowerCase().includes(query)
                )) {
                    return true;
                }
                
                return false;
            });
            
            displayResults(threadResults);
        }
        
        // Add event listeners
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        // Add click event listener to the search button
        const searchButton = document.getElementById('search-button');
        if (searchButton) {
            searchButton.addEventListener('click', performSearch);
        }
    }
    
    function displayResults(threads) {
        const searchResults = document.getElementById('search-results');
        
        if (threads.length === 0) {
            searchResults.innerHTML = '<p>No matching threads found.</p>';
            searchResults.style.display = 'block';
            return;
        }
        
        let html = '<div class="search-results">';
        html += `<p>Found ${threads.length} matching thread${threads.length === 1 ? '' : 's'}:</p>`;
        
        threads.forEach(thread => {
            const authors = thread.authors && thread.authors.length > 0 
                ? `by ${thread.authors.join(', ')}` 
                : 'No authors';
            
            html += `
            <div class="search-result">
                <h3><a href="${thread.url}">${escapeHtml(thread.title)}</a></h3>
                <div class="search-meta">
                    ${authors}
                </div>
            </div>
            `;
        });
        
        html += '</div>';
        searchResults.innerHTML = html;
        searchResults.style.display = 'block';
    }
    
    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .toString()
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
"""

# HTML template for the search results page
SEARCH_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results - {forum_name} Archive</title>
    <link rel="stylesheet" href="../static/style.css">
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const query = urlParams.get('q') || '';
            const page = parseInt(urlParams.get('page') || '1');
            
            // Set search query in input
            const searchInput = document.getElementById('search-query');
            if (searchInput) {
                searchInput.value = query;
            }
            
            // Load search results
            if (query) {
                performSearch(query, page);
            }
            
            // Handle search form submission
            const searchForm = document.getElementById('search-form');
            if (searchForm) {
                searchForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    const newQuery = searchInput.value.trim();
                    if (newQuery) {
                        window.location.href = `?q=${encodeURIComponent(newQuery)}`;
                    }
                });
            }
            
            async function performSearch(query, page = 1) {
                const resultsContainer = document.getElementById('search-results');
                const loadingEl = document.getElementById('loading');
                const paginationEl = document.getElementById('pagination');
                const resultsPerPage = 10;
                
                try {
                    loadingEl.style.display = 'block';
                    resultsContainer.innerHTML = '';
                    
                    // Load search index
                    const response = await fetch('../search/search_index.json');
                    const searchData = await response.json();
                    
                    // Filter and sort results by thread start date (newest first)
                    const queryLower = query.toLowerCase();
                    let allResults = searchData
                        .filter(thread => {
                            const titleMatch = thread.title && thread.title.toLowerCase().includes(queryLower);
                            const authorMatch = thread.authors && thread.authors.some(author => 
                                author && author.toLowerCase().includes(queryLower)
                            );
                            return titleMatch || authorMatch;
                        })
                        .sort((a, b) => {
                            // Sort by start_date in descending order (newest first)
                            if (!a.start_date) return 1;
                            if (!b.start_date) return -1;
                            return new Date(b.start_date) - new Date(a.start_date);
                        });
                    
                    // Pagination
                    const totalResults = allResults.length;
                    const totalPages = Math.ceil(totalResults / resultsPerPage);
                    const startIdx = (page - 1) * resultsPerPage;
                    const endIdx = startIdx + resultsPerPage;
                    const pageResults = allResults.slice(startIdx, endIdx);
                    
                    // Display results
                    if (totalResults === 0) {
                        resultsContainer.innerHTML = `<p>No results found for "${escapeHtml(query)}"</p>`;
                    } else {
                        const resultsHtml = `
                            <p>Found ${totalResults} result${totalResults === 1 ? '' : 's'} for "${escapeHtml(query)}"</p>
                            <div class="search-results">
                                ${pageResults.map(result => `
                                    <div class="search-result">
                                        <h3><a href="${escapeHtml(result.url)}">${escapeHtml(result.title)}</a></h3>
                                        <div class="search-meta">
                                            ${result.authors && result.authors.length > 0 
                                                ? `<span>By: ${result.authors.map(a => escapeHtml(a)).join(', ')}</span>` 
                                                : '<span>No author information</span>'}
                                            ${result.start_date || result.last_date ? `
                                                <div class="thread-dates">
                                                    ${result.start_date ? `<span>Started: ${formatDate(result.start_date)}</span>` : ''}
                                                    ${result.last_date && result.last_date !== result.start_date ? 
                                                        `<span>Last post: ${formatDate(result.last_date)}</span>` : ''}
                                                </div>
                                            ` : ''}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `;
                        resultsContainer.innerHTML = resultsHtml;
                        
                        // Add pagination
                        if (totalPages > 1) {
                            let paginationHtml = '<div class="pagination">';
                            
                            // Previous button
                            if (page > 1) {
                                paginationHtml += `<a href="?q=${encodeURIComponent(query)}&page=${page - 1}">&laquo; Previous</a>`;
                            }
                            
                            // Page numbers
                            for (let i = 1; i <= totalPages; i++) {
                                if (i === page) {
                                    paginationHtml += `<span class="current">${i}</span>`;
                                } else if (i === 1 || i === totalPages || (i >= page - 2 && i <= page + 2)) {
                                    paginationHtml += `<a href="?q=${encodeURIComponent(query)}&page=${i}">${i}</a>`;
                                } else if (i === page - 3 || i === page + 3) {
                                    paginationHtml += '<span class="ellipsis">...</span>';
                                }
                            }
                            
                            // Next button
                            if (page < totalPages) {
                                paginationHtml += `<a href="?q=${encodeURIComponent(query)}&page=${page + 1}">Next &raquo;</a>`;
                            }
                            
                            paginationHtml += '</div>';
                            paginationEl.innerHTML = paginationHtml;
                        }
                    }
                } catch (error) {
                    console.error('Error performing search:', error);
                    resultsContainer.innerHTML = '<p>An error occurred while performing the search. Please try again.</p>';
                } finally {
                    loadingEl.style.display = 'none';
                }
            }
            
            function formatDate(isoDate) {
                if (!isoDate) return '';
                const date = new Date(isoDate);
                return date.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            }
            
            function escapeHtml(unsafe) {
                if (!unsafe) return '';
                return unsafe
                    .toString()
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
            }
        });
    </script>
</head>
<body>
    <header>
        <h1>Search Results</h1>
        <nav>
            <a href="../index.html">Back to Archive</a>
        </nav>
    </header>
    
    <main>
        <div class="search-container">
            <form id="search-form" class="search-form">
                <input type="text" id="search-query" name="q" placeholder="Search messages..." required>
                <button type="submit">Search</button>
            </form>
            
            <div id="loading" style="display: none; text-align: center; padding: 20px;">
                <p>Searching...</p>
            </div>
            
            <div id="search-results"></div>
            <div id="pagination" class="pagination"></div>
        </div>
    </main>
    
    <footer>
        <p>Generated by Yahoo Groups Mbox to Static Website Converter</p>
    </footer>
</body>
</html>
"""
