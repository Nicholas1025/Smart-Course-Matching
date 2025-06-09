#!/usr/bin/env python3
"""
Smart Course Matching System - Flask Application
Integrates RDF data processing with SPARQL queries for course recommendations
"""

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from rdflib import Graph, Namespace
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Global variables for RDF graph and namespace
graph = None
CS = Namespace("http://example.org/courses#")

def load_ontology():
    """Load RDF ontology file into global graph"""
    global graph
    
    ontology_path = "data/ontology.rdf"
    
    try:
        if not os.path.exists(ontology_path):
            logger.error(f"RDF file not found: {ontology_path}")
            return False
        
        graph = Graph()
        graph.parse(ontology_path, format="xml")
        logger.info(f"Successfully loaded ontology: {len(graph)} triples")
        return True
    
    except Exception as e:
        logger.error(f"Error loading ontology: {str(e)}")
        return False

def normalize_interest(interest):
    """Normalize user interest input for URI construction"""
    # Remove spaces, hyphens, and convert to proper case
    normalized = interest.replace(" ", "").replace("-", "")
    # Capitalize first letter of each word for consistency
    words = []
    current_word = ""
    
    for char in normalized:
        if char.isupper() and current_word:
            words.append(current_word)
            current_word = char
        else:
            current_word += char
    
    if current_word:
        words.append(current_word)
    
    # Join words with proper capitalization
    return ''.join([word.capitalize() for word in words])

def build_sparql_query(interest):
    """Build SPARQL query by loading from external file and replacing interest"""
    normalized_interest = normalize_interest(interest)
    sparql_path = os.path.join("queries", "recommend.sparql")
    
    try:
        with open(sparql_path, "r", encoding="utf-8") as f:
            template = f.read()
        
        query = template.replace("__INTEREST__", normalized_interest)
        
        logger.info(f"SPARQL Query for '{interest}' (normalized: '{normalized_interest}'):")
        logger.info(query)
        return query
    
    except FileNotFoundError:
        logger.error(f"SPARQL file not found: {sparql_path}")
        return ""
    except Exception as e:
        logger.error(f"Failed to load SPARQL query: {e}")
        return ""

def execute_sparql_query(interest):
    """Execute SPARQL query and return results"""
    global graph
    
    if not graph:
        logger.error("Graph not loaded")
        return []
    
    try:
        query = build_sparql_query(interest)
        results = graph.query(query)
        
        courses = []
        for row in results:
            course_data = {
                'code': str(row.courseCode),
                'title': str(row.courseTitle),
                'uri': str(row.courseURI),
                'credits': str(row.credits),
                'yearOffered': str(row.yearOffered),
                'level': str(row.level)
            }
            courses.append(course_data)
        
        logger.info(f"Found {len(courses)} courses for interest: {interest}")
        return courses
    
    except Exception as e:
        logger.error(f"Error executing SPARQL query: {str(e)}")
        return []

def get_available_domains():
    """Get all available interest domains from the ontology using external SPARQL file"""
    global graph
    
    if not graph:
        return []
    
    sparql_path = os.path.join("queries", "domains.sparql")
    
    try:
        with open(sparql_path, "r", encoding="utf-8") as f:
            query = f.read()
        
        results = graph.query(query)
        domains = []
        
        for row in results:
            domain_uri = str(row.domain)
            # Extract domain name from URI
            domain_name = domain_uri.replace("http://example.org/courses#", "")
            # Add spaces to camelCase for better readability
            readable_name = ''.join([' ' + c if c.isupper() and i > 0 else c 
                                   for i, c in enumerate(domain_name)])
            domains.append({
                'name': domain_name,
                'readable': readable_name.strip()
            })
        
        return domains
    
    except FileNotFoundError:
        logger.error(f"SPARQL file not found: {sparql_path}")
        return []
    except Exception as e:
        logger.error(f"Error getting domains: {str(e)}")
        return []

def get_course_prerequisites(course_uri):
    """Get prerequisites for a specific course using external SPARQL file"""
    global graph
    
    if not graph:
        return []
    
    sparql_path = os.path.join("queries", "prerequisites.sparql")
    
    try:
        with open(sparql_path, "r", encoding="utf-8") as f:
            template = f.read()
        
        query = template.replace("__COURSE_URI__", course_uri)
        results = graph.query(query)
        prerequisites = []
        
        for row in results:
            prereq_data = {
                'code': str(row.prereqCode),
                'title': str(row.prereqTitle)
            }
            prerequisites.append(prereq_data)
        
        return prerequisites
    
    except FileNotFoundError:
        logger.error(f"SPARQL file not found: {sparql_path}")
        return []
    except Exception as e:
        logger.error(f"Error getting prerequisites: {str(e)}")
        return []

@app.route('/')
def index():
    """Home page with search form"""
    domains = get_available_domains()
    return render_template('index.html', domains=domains)

@app.route('/search', methods=['POST'])
def search():
    """Handle course search request"""
    interest = request.form.get('interest', '').strip()
    
    if not interest:
        flash('Please enter an interest domain.', 'error')
        return redirect(url_for('index'))
    
    # Execute SPARQL query
    courses = execute_sparql_query(interest)
    
    # Add prerequisites to each course
    for course in courses:
        course['prerequisites'] = get_course_prerequisites(course['uri'])
    
    # Get available domains for the search form
    domains = get_available_domains()
    
    return render_template('results.html', 
                         courses=courses, 
                         interest=interest,
                         domains=domains)

@app.route('/api/search')
def api_search():
    """API endpoint for course search"""
    interest = request.args.get('interest', '').strip()
    
    if not interest:
        return jsonify({'error': 'Interest parameter is required'}), 400
    
    courses = execute_sparql_query(interest)
    
    # Add prerequisites to each course
    for course in courses:
        course['prerequisites'] = get_course_prerequisites(course['uri'])
    
    return jsonify({
        'interest': interest,
        'courses': courses,
        'total': len(courses)
    })

@app.route('/api/domains')
def api_domains():
    """API endpoint to get available domains"""
    domains = get_available_domains()
    return jsonify({'domains': domains})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    global graph
    
    status = {
        'status': 'healthy' if graph else 'unhealthy',
        'graph_loaded': graph is not None,
        'triples_count': len(graph) if graph else 0
    }
    
    return jsonify(status)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

# Initialize the application
def check_sparql_files():
    """Check if all required SPARQL files exist"""
    required_files = [
        "queries/recommend.sparql",
        "queries/domains.sparql", 
        "queries/prerequisites.sparql"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing SPARQL files: {missing_files}")
        return False
    
    logger.info("All SPARQL files found successfully")
    return True

def init_app():
    """Initialize the application"""
    logger.info("Initializing Smart Course Matching System...")
    
    # Check SPARQL files first
    if not check_sparql_files():
        logger.error("Missing required SPARQL files. Please ensure all files are in the queries/ directory.")
        return False
    
    if not load_ontology():
        logger.error("Failed to load ontology. Please check the RDF file.")
        return False
    
    logger.info("Application initialized successfully!")
    return True

if __name__ == '__main__':
    # Initialize the app
    if init_app():
        # Run the Flask development server
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        logger.error("Failed to initialize application. Exiting...")
        exit(1)