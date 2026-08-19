-- AI Resume Analyzer — Seed Data
-- Job roles with required skills for the recommendation engine

INSERT OR IGNORE INTO job_roles (title, industry, required_skills_json, experience_level, description) VALUES
('Software Engineer', 'Technology', '["Python", "Java", "SQL", "Git", "Data Structures", "Algorithms", "REST APIs", "Agile"]', 'Mid', 'Design, develop, and maintain software applications.'),
('Data Scientist', 'Technology', '["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization", "Deep Learning", "R", "TensorFlow"]', 'Mid', 'Analyze complex data sets to drive business decisions.'),
('Frontend Developer', 'Technology', '["JavaScript", "HTML", "CSS", "React", "TypeScript", "Git", "REST APIs", "Responsive Design"]', 'Mid', 'Build responsive and interactive user interfaces.'),
('Backend Developer', 'Technology', '["Python", "Java", "SQL", "REST APIs", "Docker", "Git", "AWS", "PostgreSQL"]', 'Mid', 'Build and maintain server-side applications and APIs.'),
('DevOps Engineer', 'Technology', '["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Python", "Git", "Terraform"]', 'Senior', 'Manage infrastructure and deployment pipelines.'),
('Data Analyst', 'Technology', '["SQL", "Python", "Excel", "Data Visualization", "Statistics", "Tableau", "Power BI"]', 'Entry', 'Analyze data and create reports to support business decisions.'),
('Machine Learning Engineer', 'Technology', '["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "SQL", "Docker", "AWS"]', 'Senior', 'Design and deploy machine learning models at scale.'),
('Product Manager', 'Technology', '["Product Strategy", "Agile", "Data Analysis", "User Research", "A/B Testing", "SQL", "Roadmapping"]', 'Senior', 'Define product vision and strategy.'),
('UX Designer', 'Design', '["User Research", "Wireframing", "Prototyping", "Figma", "UI Design", "Usability Testing", "Design Systems"]', 'Mid', 'Design intuitive user experiences for digital products.'),
('Full Stack Developer', 'Technology', '["JavaScript", "Python", "React", "Node.js", "SQL", "Git", "REST APIs", "AWS", "Docker"]', 'Mid', 'Build end-to-end features across frontend and backend.'),
('Cloud Architect', 'Technology', '["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Networking", "Security"]', 'Senior', 'Design and implement cloud infrastructure solutions.'),
('Cybersecurity Analyst', 'Technology', '["Network Security", "Python", "Linux", "SIEM", "Penetration Testing", "Firewalls", "Risk Assessment"]', 'Mid', 'Protect organizational systems and data from security threats.'),
('Business Analyst', 'Business', '["SQL", "Excel", "Data Analysis", "Requirements Gathering", "Process Modeling", "Agile", "Stakeholder Management"]', 'Mid', 'Bridge the gap between business needs and technology solutions.'),
('Project Manager', 'Business', '["Project Planning", "Agile", "Scrum", "Risk Management", "Stakeholder Management", "JIRA", "MS Project"]', 'Senior', 'Plan and execute projects to deliver business value.'),
('Technical Writer', 'Technology', '["Technical Writing", "Documentation", "API Documentation", "Markdown", "Git", "Content Management"]', 'Mid', 'Create clear, concise technical documentation.'),
('QA Engineer', 'Technology', '["Testing", "Python", "Selenium", "Automation", "SQL", "Agile", "JIRA", "API Testing"]', 'Mid', 'Ensure software quality through testing and automation.'),
('Data Engineer', 'Technology', '["Python", "SQL", "ETL", "Apache Spark", "AWS", "Docker", "Data Warehousing", "Airflow"]', 'Mid', 'Build and maintain data pipelines and infrastructure.'),
('Mobile Developer', 'Technology', '["Swift", "Kotlin", "iOS", "Android", "Git", "REST APIs", "Firebase", "UI Design"]', 'Mid', 'Develop mobile applications for iOS and Android platforms.'),
('AI Engineer', 'Technology', '["Python", "Machine Learning", "NLP", "Computer Vision", "TensorFlow", "PyTorch", "Docker", "AWS"]', 'Senior', 'Build and deploy AI-powered applications and services.'),
('IT Support Specialist', 'Technology', '["Networking", "Windows", "Linux", "Troubleshooting", "Customer Service", "Active Directory", "Hardware"]', 'Entry', 'Provide technical support and maintain IT infrastructure.'),
('Database Administrator', 'Technology', '["SQL", "PostgreSQL", "MySQL", "Database Design", "Performance Tuning", "Backup", "Security"]', 'Mid', 'Manage and maintain database systems.'),
('Site Reliability Engineer', 'Technology', '["Linux", "Python", "Kubernetes", "Docker", "AWS", "Monitoring", "CI/CD", "Incident Response"]', 'Senior', 'Ensure reliability and performance of production systems.'),
('Research Scientist', 'Technology', '["Python", "Machine Learning", "Statistics", "Research Methods", "Scientific Computing", "Deep Learning", "Publications"]', 'Senior', 'Conduct research and develop novel algorithms and methods.'),
('Engineering Manager', 'Technology', '["Team Leadership", "Agile", "Project Management", "Code Review", "Architecture", "Mentoring", "Strategic Planning"]', 'Lead', 'Lead engineering teams to deliver high-quality software products.'),
('Solutions Architect', 'Technology', '["System Design", "AWS", "Microservices", "API Design", "Security", "Database Design", "Cloud Architecture"]', 'Senior', 'Design and oversee implementation of technical solutions.');