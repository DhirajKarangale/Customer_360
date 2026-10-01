-- 1. Use the Account Admin role
USE ROLE ACCOUNTADMIN;

-- 2. Create the Database
CREATE DATABASE IF NOT EXISTS CHURN360_DB;

-- 3. Create the Schema
CREATE SCHEMA IF NOT EXISTS CHURN360_DB.PUBLIC;

-- 4. Create an Image Repository to hold the Docker container
CREATE IMAGE REPOSITORY IF NOT EXISTS CHURN360_DB.PUBLIC.CHURN360_REPO;

-- 5. Create a Compute Pool (Requires non-trial account to start services)
CREATE COMPUTE POOL IF NOT EXISTS CHURN360_COMPUTE_POOL
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_XS
  AUTO_RESUME = TRUE
  AUTO_SUSPEND_SECS = 120;

-- 6. Grant permissions to bind the public endpoint
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE ACCOUNTADMIN;

-- 7. Get your repository URL
-- Note the 'repository_url' from this output. You'll need it for Docker push.
SHOW IMAGE REPOSITORIES IN SCHEMA CHURN360_DB.PUBLIC;

-- (At this point, you build and push the Docker container to the repository_url)
-- Example: 
-- docker build --platform linux/amd64 -t frontend .
-- docker tag frontend <repository_url>/frontend:latest
-- docker push <repository_url>/frontend:latest

-- 8. Create the Service to run the Container
CREATE SERVICE CHURN360_DB.PUBLIC.CHURN360_UI_SERVICE
  IN COMPUTE POOL CHURN360_COMPUTE_POOL
  FROM SPECIFICATION $$
    spec:
      containers:
      - name: frontend
        image: /churn360_db/public/churn360_repo/frontend:latest
      endpoints:
      - name: web
        port: 8000
        public: true
  $$;

-- 9. Check the status of the service
SELECT SYSTEM$GET_SERVICE_STATUS('CHURN360_DB.PUBLIC.CHURN360_UI_SERVICE');

-- 10. Get the public URL endpoint
SHOW ENDPOINTS IN SERVICE CHURN360_DB.PUBLIC.CHURN360_UI_SERVICE;
