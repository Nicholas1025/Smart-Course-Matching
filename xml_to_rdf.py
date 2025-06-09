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
    title = course.findtext("title")
    domain = course.findtext("domain")
    prerequisite = course.findtext("prerequisite")
    credits = course.findtext("credits")
    year = course.findtext("yearOffered")
    level = course.findtext("level")

    course_uri = URIRef(f"{CS}{code}")
    g.add((course_uri, CS.code, Literal(code)))
    g.add((course_uri, CS.title, Literal(title)))
    g.add((course_uri, CS.hasDomain, URIRef(f"{CS}{domain}")))

    if prerequisite:
        prereq_uri = URIRef(f"{CS}{prerequisite}")
        g.add((course_uri, CS.hasPrerequisite, prereq_uri))

    # Add new fields
    if credits:
        g.add((course_uri, CS.credits, Literal(credits)))
    if year:
        g.add((course_uri, CS.yearOffered, Literal(year)))
    if level:
        g.add((course_uri, CS.level, Literal(level)))

# Serialize RDF graph
g.serialize("data/ontology.rdf", format="xml")
print("✅ RDF generated with credits, year, and level!")
