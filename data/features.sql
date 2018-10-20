SET SQL_SAFE_UPDATES=0;

DROP TABLE IF EXISTS `features`;

CREATE TABLE `features` (
  `company_name` VARCHAR(255) ,	
  `category_code` VARCHAR(32) ,	  
  `company_id` VARCHAR(64) NOT NULL,
  PRIMARY KEY (`company_id`));  

INSERT INTO features ( company_name, category_code, company_id ) SELECT name, category_code, id FROM cb_objects where entity_type='Company';

# funding rounds
ALTER TABLE features ADD funding_rounds BIGINT after company_id;
UPDATE features SET funding_rounds = 0;
UPDATE features dest, 
	(SELECT object_id, count(funding_round_id) as funding_rounds FROM cb_funding_rounds group by object_id) src
    SET dest.funding_rounds = src.funding_rounds 
    where dest.company_id = src.object_id;

# investments by company
ALTER TABLE features ADD investments BIGINT after company_id;
UPDATE features SET investments = 0;
UPDATE features dest, 
	(SELECT investor_object_id, count(funded_object_id) as investments FROM cb_investments group by investor_object_id) AS src
    SET dest.investments = src.investments 
    where dest.company_id = src.investor_object_id;  

# acquisitions by company
ALTER TABLE features ADD acquisitions_cost BIGINT after company_id;
UPDATE features SET acquisitions_cost = 0;
ALTER TABLE features ADD acquisitions BIGINT after company_id;
UPDATE features SET acquisitions = 0;
UPDATE features dest, 
	(SELECT acquiring_object_id , count(acquired_object_id) AS acquisitions , SUM(price_amount) AS acquisitions_cost FROM cb_acquisitions group by acquiring_object_id) AS src
    SET dest.acquisitions = src.acquisitions , dest.acquisitions_cost = src.acquisitions_cost
    where dest.company_id = src.acquiring_object_id;

# Number of VCs, PEs investing inthe company
ALTER TABLE features ADD investors BIGINT after company_id;
UPDATE features SET investors = 0;
UPDATE features dest, 
	(SELECT funded_object_id, count(investor_object_id) as investors  from (SELECT distinctrow funded_object_id,  investor_object_id  FROM cb_investments) AS src GROUP BY funded_object_id) AS src
    SET dest.investors = src.investors
    where dest.company_id = src.funded_object_id;

# Number Finance people in the company
ALTER TABLE features ADD finance_people BIGINT after company_id;
UPDATE features SET finance_people = 0;
UPDATE features dest, 
	(SELECT count(person_object_id)  AS finance_people, relationship_object_id as company_id FROM cb_relationships r where title like '%Fin%' group by relationship_object_id) AS src
    SET dest.finance_people = src.finance_people
    where dest.company_id = src.company_id;


commit;

SELECT * from features where investors >0 AND acquisitions > 0 AND acquisitions_cost> 0 AND investments > 0 AND  funding_rounds > 0;

SELECT * from features where finance_people > 0;


# Number of employees
ALTER TABLE features ADD employee BIGINT after finance_people;
UPDATE features SET employee = 0;
UPDATE features dest, 
	(SELECT id, relationships as employee FROM cb_objects) src
    SET dest.employee = src.employee 
    where dest.company_id = src.id;

# Company age (months)
ALTER TABLE features ADD company_age BIGINT after employee;
UPDATE features SET company_age = 0;
UPDATE features dest, 
	(SELECT id, period_diff(date_format(current_date(),'%Y%m'),date_format(founded_at,'%Y%m')) as company_age FROM cb_objects where founded_at is not null) src
    SET dest.company_age = src.company_age 
    where dest.company_id = src.id;

# Number of milestones
ALTER TABLE features ADD milestones BIGINT after company_age;
UPDATE features SET milestones = 0;
UPDATE features dest, 
	(SELECT id, milestones FROM cb_objects) src
    SET dest.milestones = src.milestones 
    where dest.company_id = src.id;

# Number of revisions on profiles
ALTER TABLE features ADD revisions BIGINT after milestones;
UPDATE features SET revisions = 0;

# Number of arcticles on techcrunch
ALTER TABLE features ADD techcrunch BIGINT after revisions;
UPDATE features SET techcrunch = 0;
UPDATE features dest, 
	(select object_id, count(1) as techcrunch from cb_milestones where description like '%techcrunch%' group by object_id) src
    SET dest.techcrunch = src.techcrunch 
    where dest.company_id = src.object_id;

# Number of competitors
ALTER TABLE features ADD competitors BIGINT after techcrunch;
UPDATE features SET competitors = 0;
UPDATE features dest, 
	(select category_code, count(1)-1 as tot from cb_objects group by category_code) src
    SET dest.competitors = src.tot 
    where dest.category_code = src.category_code;

# Add the acquired field
ALTER TABLE features ADD acquired BOOLEAN after competitors;
UPDATE features SET acquired = 0;
UPDATE features dest, 
	(select id from cb_objects where status = 'acquired') src
    SET dest.acquired = 1 
    where dest.company_id = src.id;

# Number of competitors acquired
ALTER TABLE features ADD competitors_acquired BIGINT after competitors;
UPDATE features SET competitors_acquired = 0;
UPDATE features dest, 
	(select category_code, count(1) as tot from cb_objects where status = 'acquired'
group by category_code) src
    SET dest.competitors_acquired = src.tot 
    where dest.category_code = src.category_code;

UPDATE features SET competitors_acquired = competitors_acquired-1 where acquired = 1;

# Number of offices
ALTER TABLE features ADD offices BIGINT after competitors_acquired;
UPDATE features SET offices = 0;
UPDATE features dest, 
	(select object_id, count(1) as tot from cb_offices group by object_id) src
    SET dest.offices = src.tot 
    where dest.company_id = src.object_id;

# Number of products
ALTER TABLE features ADD products BIGINT after offices;
UPDATE features SET products = 0;
UPDATE features dest, 
	(select parent_id, count(1) as tot from cb_objects where entity_type = 'Product'
group by parent_id) src
    SET dest.products = src.tot 
    where dest.company_id = src.parent_id;

# Number of providers
ALTER TABLE features ADD providers BIGINT after products;
UPDATE features SET providers = 0;
UPDATE features dest, 
	(select relationship_object_id, count(1) as tot from cb_relationships where title like '%Provider%' group by relationship_object_id) src
    SET dest.providers = src.tot
    where dest.company_id = src.relationship_object_id;

# averge number of investors per round
ALTER TABLE features ADD avg_funding_rounds_investors BIGINT after providers;
UPDATE features SET avg_funding_rounds_investors = 0;
UPDATE features dest, 
(select src1.funded_object_id, avg(src1.tot) as tt from
(select funding_round_id, funded_object_id, count(1) as tot
from cb_investments
group by funding_round_id, funded_object_id) src1
group by src1.funded_object_id ) src2
set dest.avg_funding_rounds_investors = src2.tt
where dest.company_id = src2.funded_object_id;

# average number of funding per round(in usd)
ALTER TABLE features ADD avg_funding BIGINT after avg_funding_rounds_investors;
UPDATE features SET avg_funding = 0;
UPDATE features dest, 
(select object_id, avg(raised_amount_usd) as avg_funding
from cb_funding_rounds
group by object_id) src
set dest.avg_funding = src.avg_funding
where dest.company_id = src.object_id;

# Number of founders
ALTER TABLE features ADD founders BIGINT after avg_funding;
UPDATE features SET founders = 0;
UPDATE features dest, 
	(select relationship_object_id, count(1) as tot from cb_relationships where title like '%Founder%' group by relationship_object_id) src
    SET dest.founders = src.tot
    where dest.company_id = src.relationship_object_id;

# Number of founders for successful companies(ipos)
ALTER TABLE features ADD succ_founders BIGINT after founders;
UPDATE features SET succ_founders = 0;
UPDATE features dest, 
(select a.relationship_object_id, count(1) as tot 
from cb_relationships a, cb_ipos b
where a.title like '%Founder%'
and a.relationship_object_id = b.object_id
group by a.relationship_object_id) src
set dest.succ_founders = src.tot
where dest.company_id = src.relationship_object_id;

UPDATE features dest, 
(select a.relationship_object_id, count(1) as tot 
from cb_relationships a, cb_acquisitions b
where a.title like '%Founder%'
and a.relationship_object_id = b.acquired_object_id
group by a.relationship_object_id) src
set dest.succ_founders = src.tot
where dest.company_id = src.relationship_object_id;

# founder experience per month (max one)
ALTER TABLE features ADD founders_exp BIGINT after succ_founders;
UPDATE features SET founders_exp = 0;
UPDATE features dest, 
(select b.relationship_object_id, 
max(period_diff(date_format(current_date(),'%Y%m'),date_format(a.graduated_at,'%Y%m'))) as exp
from cb_degrees a, cb_relationships b
where b.title like '%Founder%'
and b.person_object_id = a.object_id
group by b.relationship_object_id) src
set dest.founders_exp = src.exp
where dest.company_id = src.relationship_object_id;




