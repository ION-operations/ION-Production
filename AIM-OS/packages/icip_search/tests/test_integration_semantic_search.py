"""
Integration Tests: Complete Semantic Search Flow
"""

import pytest
import tempfile
from icip_search import SemanticEngine


@pytest.fixture
def realistic_codebase(tmp_path):
    """Create realistic code files"""
    
    # Authentication module
    (tmp_path / "auth.py").write_text('''
def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user with username and password"""
    user = find_user(username)
    return verify_password(user, password)

def verify_credentials(username, password):
    """Verify user credentials"""
    return check_database(username, password)

def login_user(user_id: int):
    """Create login session for user"""
    session = create_session(user_id)
    return session.token
''')
    
    # API module
    (tmp_path / "api.py").write_text('''
async def fetch_data(endpoint: str):
    """Fetch data from API endpoint"""
    response = await http_client.get(endpoint)
    return response.json()

async def post_data(endpoint: str, data: dict):
    """Post data to API"""
    response = await http_client.post(endpoint, json=data)
    return response.status_code
''')
    
    # Database module
    (tmp_path / "database.py").write_text('''
def query_database(sql: str):
    """Execute SQL query"""
    connection = get_connection()
    return connection.execute(sql)

def save_to_database(table: str, data: dict):
    """Save data to database table"""
    return insert(table, data)
''')
    
    return str(tmp_path)


def test_end_to_end_semantic_search(realistic_codebase):
    """Test complete semantic search flow"""
    # Create engine
    engine = SemanticEngine(realistic_codebase)
    
    # Index codebase
    engine.index_codebase(languages=['py'])
    
    # Should have indexed all functions
    assert engine.index.size() >= 7  # 7 functions defined
    
    # Search for authentication
    results = engine.search("user authentication and login", k=5)
    
    assert len(results) > 0
    
    # Top results should be auth-related
    top_names = {r.name for r in results[:3]}
    assert 'authenticate_user' in top_names or 'login_user' in top_names or 'verify_credentials' in top_names


def test_semantic_vs_literal_difference(realistic_codebase):
    """Test that semantic search finds what literal wouldn't"""
    engine = SemanticEngine(realistic_codebase)
    engine.index_codebase(languages=['py'])
    
    # Search for "login" (word not in "authenticate_user" function name)
    results = engine.search("login functionality", k=10)
    
    # Semantic search should find authenticate_user even though it doesn't contain "login"
    result_codes = ' '.join([r.code for r in results])
    assert 'authenticate' in result_codes.lower()


def test_synonym_detection(realistic_codebase):
    """Test that semantic search understands synonyms"""
    engine = SemanticEngine(realistic_codebase)
    engine.index_codebase(languages=['py'])
    
    # "fetch" and "get" are synonyms for API calls
    results_fetch = engine.search("fetch from API", k=5)
    results_get = engine.search("get from API", k=5)
    
    # Both should find API-related code
    assert len(results_fetch) > 0
    assert len(results_get) > 0
    
    # Should have overlap (finding same functions)
    names_fetch = {r.name for r in results_fetch}
    names_get = {r.name for r in results_get}
    overlap = names_fetch & names_get
    assert len(overlap) > 0


def test_relevance_ranking(realistic_codebase):
    """Test that results are ranked by relevance"""
    engine = SemanticEngine(realistic_codebase)
    engine.index_codebase(languages=['py'])
    
    results = engine.search("database queries", k=10)
    
    # Relevance should decrease
    relevances = [r.relevance for r in results]
    for i in range(len(relevances) - 1):
        assert relevances[i] >= relevances[i + 1]
    
    # Top result should be about database
    assert 'database' in results[0].file or 'query' in results[0].name.lower()


def test_context_included(realistic_codebase):
    """Test that context is included in results"""
    engine = SemanticEngine(realistic_codebase)
    engine.index_codebase(languages=['py'])
    
    results = engine.search("authentication", k=5, include_context=True)
    
    # Results should have context
    assert all(r.context is not None for r in results)
    
    # Context should be longer than code
    for result in results:
        if result.context:
            assert len(result.context) >= len(result.code)


def test_multiple_languages(tmp_path):
    """Test handling multiple file types"""
    # Create files
    (tmp_path / "file.py").write_text("def func(): pass")
    (tmp_path / "file.js").write_text("function func() {}")
    (tmp_path / "file.txt").write_text("not code")
    
    engine = SemanticEngine(str(tmp_path))
    engine.index_codebase(languages=['py'])
    
    # Should only index Python files
    assert engine.index.size() >= 1
    assert all(c.language == 'python' for c in engine.chunks)


def test_performance_acceptable(realistic_codebase):
    """Test that search performance is acceptable"""
    import time
    
    engine = SemanticEngine(realistic_codebase)
    engine.index_codebase(languages=['py'])
    
    # Measure search time
    start = time.time()
    results = engine.search("database operations", k=20)
    duration = time.time() - start
    
    # Should be fast (<500ms target, but likely <100ms)
    assert duration < 0.5  # 500ms
    assert len(results) > 0

