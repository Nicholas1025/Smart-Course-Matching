#!/usr/bin/env python3
"""
Smart Course Matching System - Flask Application
Integrates RDF data processing with SPARQL queries for course recommendations
Updated to support Computing, Business, and Law departments
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
    return interest.strip()

def build_sparql_query(interest):
    sparql_path = os.path.join("queries", "recommend.sparql")

    try:
        with open(sparql_path, "r", encoding="utf-8") as f:
            template = f.read()

        interest_lower = interest.lower()

        # Updated keyword mapping to include Business and Law programs
        keyword_map = {
            # Computing Department
            "artificial intelligence": "artificial intelligence",
            "security technology": "security technology", 
            "data communications": "data communications and networking",
            "bioinformatics": "bioinformatics",
            "business intelligence and analytics": "business intelligence and analytics",
            "computer graphics": "computer graphics",
            "database systems": "database",
            "cybersecurity": "cybersecurity",
            "web development": "web development",
            "data mining": "data mining",
            
            # Business Department
            "business administration": "business administration",
            "accounting": "accounting",
            "management": "management",
            "marketing": "marketing",
            "finance": "finance",
            "human resource": "human resource",
            "operations management": "operations",
            "strategic management": "strategic",
            "international business": "international business",
            
            # Law Department
            "law": "law",
            "legal studies": "legal",
            "constitutional law": "constitutional",
            "contract law": "contract",
            "criminal law": "criminal",
            "tort law": "tort",
            "administrative law": "administrative",
            "corporate law": "corporate",
            "intellectual property": "intellectual property",
            "family law": "family",
            "environmental law": "environmental"
        }

        keyword = ""
        for full, short in keyword_map.items():
            if full in interest_lower:
                keyword = short
                break

        # Fallback: use last two words if no specific mapping found
        if not keyword:
            keyword = " ".join(interest_lower.split()[-2:])

        # Replace placeholder in SPARQL template
        query = template.replace("__INTEREST__", keyword.lower())

        logger.info(f"[DEBUG] Final SPARQL query:\n{query}")
        return query

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
                'uri': str(row.courseURI),
                'code': str(row.code),
                'name': str(row.name),
                'type': str(row.type),
                'synopsis': str(row.synopsis),
                'version': str(row.version),
                'academicStaff': str(row.academicStaff),
                'semester': str(row.semester),
                'credits': str(row.credits),
                'prerequisite': str(row.prerequisite),
                'department': str(row.department) if hasattr(row, 'department') else 'Unknown'
            }
            courses.append(course_data)

        logger.info(f"[DEBUG] User selected interest: {interest}")
        logger.info(f"[DEBUG] Normalized interest: {normalize_interest(interest)}")
        logger.info(f"Found {len(courses)} courses for interest: {interest}")
        return courses
    
    except Exception as e:
        logger.error(f"Error executing SPARQL query: {str(e)}")
        return []

def get_available_types():
    """Extract unique course programs from RDF cs:type - updated for all departments"""
    global graph
    if not graph:
        return []

    sparql_path = os.path.join("queries", "types.sparql")
    try:
        with open(sparql_path, "r", encoding="utf-8") as f:
            query = f.read()
        results = graph.query(query)

        types = set()

        for row in results:
            type_value = str(row.type)

            # Extract after "for" if exists
            if "for" in type_value:
                specialization_str = type_value.split("for", 1)[1].strip()

                # Updated known programs to include Business and Law
                known_programs = [
                    # Computing Programs
                    "B.CS (Hons) Artificial Intelligence",
                    "B.IT (Hons) Artificial Intelligence", 
                    "B.IT (Hons) Data Communications and Networking",
                    "B.IT (Hons) Security Technology",
                    "B.Sc (Hons) Bioinformatics",
                    "B.IT (Hons) Business Intelligence and Analytics",
                    
                    # Business Programs
                    "B.BA (Hons) Business Administration",
                    "B.ACC (Hons) Accounting",
                    
                    # Law Programs
                    "LLB (Hons) Law"
                ]

                for prog in known_programs:
                    if prog in specialization_str:
                        types.add(prog)

            else:
                clean = type_value.strip()
                if clean:
                    types.add(clean)

        return sorted(types)

    except Exception as e:
        logger.error(f"Error retrieving course types: {e}")
        return []

def get_departments():
    """Get available departments"""
    global graph
    if not graph:
        return []
    
    try:
        # SPARQL query to get distinct departments
        query = """
        PREFIX cs: <http://example.org/courses#>
        SELECT DISTINCT ?department
        WHERE {
            ?course cs:department ?department .
        }
        ORDER BY ?department
        """
        
        results = graph.query(query)
        departments = [str(row.department) for row in results]
        return departments
        
    except Exception as e:
        logger.error(f"Error retrieving departments: {e}")
        return ['Computing', 'Business', 'Law']  # Fallback

def get_courses_by_department(department):
    """Get courses filtered by department"""
    global graph
    if not graph:
        return []
    
    try:
        query = f"""
        PREFIX cs: <http://example.org/courses#>
        SELECT ?courseURI ?code ?name ?type ?synopsis ?version ?academicStaff ?semester ?credits ?prerequisite ?department
        WHERE {{
            ?courseURI cs:code ?code ;
                      cs:name ?name ;
                      cs:type ?type ;
                      cs:synopsis ?synopsis ;
                      cs:version ?version ;
                      cs:academicStaff ?academicStaff ;
                      cs:semester ?semester ;
                      cs:credits ?credits ;
                      cs:prerequisite ?prerequisite ;
                      cs:department ?department .
            FILTER(?department = "{department}")
        }}
        ORDER BY ?code
        """
        
        results = graph.query(query)
        courses = []
        
        for row in results:
            course_data = {
                'uri': str(row.courseURI),
                'code': str(row.code),
                'name': str(row.name),
                'type': str(row.type),
                'synopsis': str(row.synopsis),
                'version': str(row.version),
                'academicStaff': str(row.academicStaff),
                'semester': str(row.semester),
                'credits': str(row.credits),
                'prerequisite': str(row.prerequisite),
                'department': str(row.department)
            }
            courses.append(course_data)
        
        return courses
        
    except Exception as e:
        logger.error(f"Error getting courses by department: {e}")
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
    types = get_available_types()
    departments = get_departments()
    return render_template('index.html', types=types, departments=departments)

@app.route('/search', methods=['POST'])
def search():
    """Handle course search request"""
    interest = request.form.get('interest', '').strip()
    
    if not interest:
        flash('Please select a course type.', 'error')
        return redirect(url_for('index'))
    
    courses = execute_sparql_query(interest)
    
    for course in courses:
        course['prerequisites'] = get_course_prerequisites(course['uri'])
    
    types = get_available_types()
    departments = get_departments()
    
    return render_template('results.html', 
                           courses=courses, 
                           interest=interest,
                           types=types,
                           departments=departments)

@app.route('/department/<department_name>')
def department_courses(department_name):
    """Show courses by department"""
    courses = get_courses_by_department(department_name)
    
    for course in courses:
        course['prerequisites'] = get_course_prerequisites(course['uri'])
    
    departments = get_departments()
    
    return render_template('department.html',
                          courses=courses,
                          department=department_name,
                          departments=departments)

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

@app.route('/api/types')
def api_types():
    """API endpoint to get available course types"""
    types = get_available_types()
    return jsonify({'types': types})

@app.route('/api/departments')
def api_departments():
    """API endpoint to get available departments"""
    departments = get_departments()
    return jsonify({'departments': departments})

@app.route('/api/department/<department_name>')
def api_department_courses(department_name):
    """API endpoint to get courses by department"""
    courses = get_courses_by_department(department_name)
    
    # Add prerequisites to each course
    for course in courses:
        course['prerequisites'] = get_course_prerequisites(course['uri'])
    
    return jsonify({
        'department': department_name,
        'courses': courses,
        'total': len(courses)
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    global graph
    
    status = {
        'status': 'healthy' if graph else 'unhealthy',
        'graph_loaded': graph is not None,
        'triples_count': len(graph) if graph else 0,
        'departments': get_departments() if graph else []
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
        "queries/types.sparql", 
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
    logger.info(f"Available departments: {get_departments()}")
    return True

if __name__ == '__main__':
    # Initialize the app
    if init_app():
        # Run the Flask development server
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        logger.error("Failed to initialize application. Exiting...")
        exit(1)