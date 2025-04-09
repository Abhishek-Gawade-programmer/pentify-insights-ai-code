
-- sample queries

-- 3. Join projects with companies to get project details with company information
SELECT 
    p.id AS project_id,
    p.project_name,
    p.status,
    p.budget_type,
    p.currency,
    p.deadline,
    p.description,
    c.name AS company_name,
    c.email,
    c.phone,
    c.address_city,
    c.address_country,
    c.website
FROM 
    public.projects p
JOIN 
    public.companies c ON p.company_id = c.contact_id
WHERE 
    p.status = 'active';

-- 4. Find all projects for a specific company
SELECT 
    p.id,
    p.project_name,
    p.deadline,
    p.status,
    p.manager_email
FROM 
    public.projects p
JOIN 
    public.companies c ON p.company_id = c.contact_id
WHERE 
    c.name = 'Collaborate Global';

-- 5. Get all companies with active projects
SELECT DISTINCT
    c.name,
    c.email,
    c.phone,
    c.address_country
FROM 
    public.companies c
JOIN 
    public.projects p ON c.contact_id = p.company_id
WHERE 
    p.status = 'active';

-- 6. Count projects by company
SELECT 
    c.name AS company_name,
    COUNT(p.id) AS project_count
FROM 
    public.companies c
JOIN 
    public.projects p ON c.contact_id = p.company_id
GROUP BY 
    c.name
ORDER BY 
    project_count DESC;


-- 2. Get all products that have been sold
-- 7. Get all quotes with company information
SELECT 
    q.id AS quote_id,
    q.quote_name,
    q.status,z
    q.sum,
    q.currency,
    q.date,
    q.deadline,
    c.name AS company_name,
    c.email AS company_email,
    c.phone AS company_phone,
    c.address_country
FROM 
    public.quotes q
JOIN 
    public.companies c ON q.company_id = c.contact_id
ORDER BY 
    q.date DESC;

-- 8. Find quotes by status with company details
SELECT 
    q.id,
    q.quote_name,
    q.sum,
    q.currency,
    q.date,
    c.name AS company_name,
    c.email AS company_email
FROM 
    public.quotes q
JOIN 
    public.companies c ON q.company_id = c.contact_id
WHERE 
    q.status = 'accepted'
ORDER BY 
    q.sum DESC;

-- 9. Get total quote value by company
SELECT 
    c.name AS company_name,
    SUM(q.sum) AS total_quote_value,
    q.currency
FROM 
    public.quotes q
JOIN 
    public.companies c ON q.company_id = c.contact_id
WHERE 
    q.is_deleted = 0
GROUP BY 
    c.name, q.currency
ORDER BY 
    total_quote_value DESC;


-- 10 get company details  via id 

SELECT * FROM companies WHERE contact_id = '123';


