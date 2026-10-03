-- ==============================================================================
-- SPCS External Access Integration Setup
-- ==============================================================================
-- Run these commands as ACCOUNTADMIN in the Snowflake UI Worksheet.
-- You must replace 'YOUR-POSTGRES-HOST' with your actual Postgres host 
-- if Postgres is external to Snowflake.
-- ==============================================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE CUSTOMER360_DB; -- Replace if deploying to a different DB
USE SCHEMA PUBLIC;

-- 1. Create a Network Rule allowing outbound traffic to your external services
CREATE OR REPLACE NETWORK RULE ai_worker_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = (
      'singapore-keyvalue.render.com:6379',                                                              -- Redis (Render)
      'api.groq.com:443',                                                                                -- Groq API
      'generativelanguage.googleapis.com:443',                                                           -- Google Gemini API
      'df2wnm7nbzfabaxdl7o2h7j7fa.xbobxlx-wo36064.ap-southeast-7.aws.postgres.snowflake.app:5432'      -- Postgres (Snowflake-managed)
  );

-- 2. Create the External Access Integration binding to the Network Rule
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION ai_worker_access_integration
  ALLOWED_NETWORK_RULES = (ai_worker_network_rule)
  ENABLED = true;

-- 3. Grant usage on the integration to the role deploying/running the SPCS service
--    Replace SYSADMIN with your actual role if different (e.g., the role used in GitHub Actions)
GRANT USAGE ON INTEGRATION ai_worker_access_integration TO ROLE SYSADMIN;
