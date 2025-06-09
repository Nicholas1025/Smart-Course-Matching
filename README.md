# 🧠 Smart Course Matching System (Semantic Web Project)

A semantic web–powered academic recommendation system that helps students find suitable university courses based on their interest domain and prerequisites. This project integrates XML, RDF/OWL, SPARQL, and Flask to demonstrate a practical application of Semantic Web Technologies in education.

---

## 📌 Features

- 🔍 Course Recommendation by interest domain (e.g., Artificial Intelligence, Data Science)
- ✅ SPARQL-powered search with external query templates
- 📘 Prerequisite tracing for each course
- 💡 Course details display: title, code, credits, year offered, level
- 🧾 Modular architecture with ontology-based data
- 🌐 Web interface using Flask + Bootstrap
- 📡 API endpoints for integration or extension
- ⚙️ Health check and error handling built-in

---

## 🗂 Project Structure

Smart-Course-Matching/
├── app.py                      # Main Flask application
├── data/
│   ├── ontology.rdf            # RDF data file generated from courses.xml
│   └── courses.xml             # Source XML file for course data
├── queries/
│   ├── recommend.sparql        # Main course recommendation query
│   ├── domains.sparql          # Domain listing query
│   └── prerequisites.sparql    # Course prerequisites query
├── templates/
│   ├── index.html              # Interest selection page
│   ├── results.html            # Course result display page
│   └── error.html              # Error display template
├── static/                     # (Optional) CSS/images if needed
├── xml_to_rdf.py               # Script to convert XML → RDF
└── requirements.txt            # Python dependencies


---

## 🚀 How to Run the Project

1. Clone the repository:
   git clone https://github.com/your-username/smart-course-matching.git

2. Navigate into the directory:
   cd smart-course-matching

3. (Optional) Create virtual environment:
   python -m venv venv
   source venv/bin/activate  # on macOS/Linux
   venv\Scripts\activate     # on Windows

4. Install dependencies:
   pip install -r requirements.txt

5. Generate RDF from XML:
   python xml_to_rdf.py

6. Run the Flask app:
   python app.py

Then open browser at: http://localhost:5000

---

## 🔎 Example Domains

| Domain                | RDF URI Tail             |
|-----------------------|--------------------------|
| Artificial Intelligence | ArtificialIntelligence |
| Data Science          | DataScience              |
| Software Engineering  | SoftwareEngineering      |

---

## 🛠 Technologies Used

| Component      | Technology       |
|----------------|------------------|
| Backend        | Python + Flask   |
| Frontend       | HTML + Bootstrap |
| Data Model     | XML + RDF        |
| Query Engine   | SPARQL (rdflib)  |
| Ontology       | OWL-based RDF    |
| Parser Tool    | xml.etree + rdflib |
| Query Structure| External SPARQL templates |

---

## ✍️ Contributors

- Nicholas Tay Jun Yang
- Loh Jia Xian
- Elysa Lee Xing Wan
- Tai Wei Zhe 

---

## 📘 Course Info

> Multimedia University (MMU)  
> TSW6223 – Semantic Web Technology  
> Semester: Trimester 3, 2025  
> Project Title: Smart Course Matching System

---

## ✅ Status

> Fully functional system with RDF-based course modeling, SPARQL-powered querying, Flask front-end, and modular ontology design. Ready for academic demonstration or extension.