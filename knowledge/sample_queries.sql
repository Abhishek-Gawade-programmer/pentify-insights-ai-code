
-- sample queries for contacts

-- Get contacts by id 
SELECT * FROM contacts WHERE contact_id = '325';

-- User can treat contact_id as person_id

-- Get quotes for that contacts use "contact_id"
SELECT * FROM quotes WHERE person_id = '123';



-- sample queries for companies

-- Get companies by id 
SELECT * FROM companies WHERE contact_id = '123';



-- Get projects for that company use "contact_id" in companies table
SELECT * FROM projects WHERE company_id = '123';



-- Get quotes for that company use "contact_id" in companies table
SELECT * FROM quotes WHERE company_id = '123';


-- sample queries for projects

-- Get projects by id 
SELECT * FROM projects WHERE id = '123';


-- Get quotes for that project use "id" in projects table
SELECT * FROM quotes WHERE project_id = '123';























