-- <query description>
-- Retrieve companies with their primary contact details.
-- Join companies and contacts using the company identifier (companies.id_code = contacts.related_company_id).
-- Display company name, website, and contact's first name, last name, and email.
-- </query description>
-- <query>
SELECT
    comp.name AS company_name,
    comp.website,
    cont.name AS contact_first_name,
    cont.lastname AS contact_last_name,
    cont.email AS contact_email
FROM
    companies comp
LEFT JOIN
    contacts cont ON comp.id = cont.related_company_id
WHERE
    comp.is_client = 1;
-- </query>


-- <query description>
-- For each project, calculate the number of quotes issued and the total quoted sum.
-- Join projects and quotes on project id (projects.id = quotes.project_id) and consider only non-deleted quotes.
-- </query description>
-- <query>
SELECT
    p.project_name,
    p.company_name,
    COUNT(q.id) AS quote_count,
    SUM(q.sum) AS total_quote_amount
FROM
    projects p
LEFT JOIN
    quotes q ON p.id = q.project_id AND q.is_deleted = 0
GROUP BY
    p.project_name, p.company_name
ORDER BY
    total_quote_amount DESC;
-- </query>


-- <query description>
-- List companies along with the number of associated contacts and projects.
-- Use subqueries to count contacts (based on companies.id_code = contacts.related_company_id)
-- and projects (based on companies.id = projects.company_id).
-- </query description>
-- <query>
SELECT
    comp.name AS company_name,
    comp.website,
    (SELECT COUNT(*)
     FROM contacts cont
     WHERE cont.related_company_id = comp.id_code) AS contact_count,
    (SELECT COUNT(*)
     FROM projects p
     WHERE p.company_id = comp.id) AS project_count
FROM
    companies comp
ORDER BY
    company_name;
-- </query>


-- <query description>
-- Retrieve detailed project information along with the primary contact from the company associated with each project.
-- Join projects with companies and then join companies with contacts.
-- Assumes companies.id_code links to contacts.related_company_id.
-- </query description>
-- <query>
SELECT
    p.project_name,
    p.deadline,
    comp.name AS company_name,
    comp.website,
    cont.name AS contact_first_name,
    cont.lastname AS contact_last_name,
    cont.email AS contact_email
FROM
    projects p
JOIN
    companies comp ON p.company_id = comp.id
LEFT JOIN
    contacts cont ON comp.id_code = cont.related_company_id
WHERE
    p.deadline > CURRENT_DATE
ORDER BY
    p.deadline;
-- </query>


-- <query description>
-- Analyze quotes by calculating average discount and total VAT per company.
-- Group quotes by company_name and filter out deleted quotes.
-- </query description>
-- <query>
SELECT
    q.company_name,
    AVG(q.discount) AS average_discount,
    SUM(q.vat_sum) AS total_vat
FROM
    quotes q
WHERE
    q.is_deleted = 0
GROUP BY
    q.company_name
ORDER BY
    total_vat DESC;
-- </query>


-- <query description>
-- Identify the top 3 companies with the highest total quoted amount across all projects.
-- Join quotes with companies (using companies.id_code = quotes.company_id if available,
-- otherwise match on company_name), and calculate the sum per company.
-- </query description>
-- <query>
SELECT
    q.company_name,
    SUM(q.sum) AS total_quote_amount
FROM
    quotes q
WHERE
    q.is_deleted = 0
GROUP BY
    q.company_name
ORDER BY
    total_quote_amount DESC
LIMIT 3;
-- </query>
