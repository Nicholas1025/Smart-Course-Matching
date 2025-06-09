import xml.etree.ElementTree as ET
from rdflib import Graph, Literal, Namespace, URIRef

# Define namespace
CS = Namespace("http://example.org/courses#")

# Initialize RDF graph
g = Graph()
g.bind("cs", CS)

# Load XML file
tree = ET.parse("data/courses.xml")
root = tree.getroot()

for course in root.findall("course"):
    code = course.findtext("code")
    name = course.findtext("name")
    course_type = course.findtext("type")
    synopsis = course.findtext("synopsis")
    version = course.findtext("version")
    academic_staff = course.findtext("academicStaff")
    semester = course.findtext("semester")
    credits = course.findtext("credits")
    prerequisite = course.findtext("prerequisite")

    course_uri = URIRef(f"{CS}{code}")

    g.add((course_uri, CS.code, Literal(code)))
    g.add((course_uri, CS.name, Literal(name)))
    g.add((course_uri, CS.type, Literal(course_type)))
    g.add((course_uri, CS.synopsis, Literal(synopsis)))
    g.add((course_uri, CS.version, Literal(version)))
    g.add((course_uri, CS.academicStaff, Literal(academic_staff)))
    g.add((course_uri, CS.semester, Literal(semester)))
    g.add((course_uri, CS.credits, Literal(credits)))
    g.add((course_uri, CS.prerequisite, Literal(prerequisite)))

# Serialize RDF graph
g.serialize("data/ontology.rdf", format="xml")
print("✅ RDF generated with full updated fields!")
