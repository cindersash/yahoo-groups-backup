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
    text-align: center;
}

.search-form {
    display: flex;
    max-width: 500px;
    margin: 0 auto 20px;
    gap: 8px;
}

#search-input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

#search-button {
    padding: 10px 20px;
    background-color: #0366d6;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

#search-button:hover {
    background-color: #0356b6;
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
        
        document.getElementById('search-button').addEventListener('click', performSearch););
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
SEARCH_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results - Yahoo Groups Archive</title>
    <link rel="stylesheet" href="../static/style.css">
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
            <div class="search-form">
                <input type="text" id="search-input" placeholder="Search messages...">
                <button id="search-button" type="button">Search</button>
            </div>
            <div id="search-results"></div>
        </div>
    </main>
    
    <footer>
        <p>Generated by Yahoo Groups Mbox to Static Website Converter</p>
    </footer>
    
    <script src="../static/script.js"></script>
</body>
</html>
"""
