-- Schema for Snowflake CoCo CLI Hackathon 2026 - Customer 360

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255),
    phone_number VARCHAR(20),
    date_of_birth DATE,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE insurance_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255),
    phone_number VARCHAR(20),
    agency_name VARCHAR(255),
    license_number VARCHAR(100) UNIQUE,
    profile_image_url VARCHAR(512),
    suggestions TEXT,
    suggestions_updated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_number VARCHAR(100) UNIQUE NOT NULL,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES insurance_agents(id) ON DELETE SET NULL,
    policy_type VARCHAR(50) NOT NULL, -- e.g., 'Life', 'Health', 'Auto', 'Home'
    status VARCHAR(50) NOT NULL, -- e.g., 'Active', 'Expired', 'Cancelled'
    start_date DATE,
    end_date DATE,
    premium_amount DECIMAL(10, 2),
    coverage_amount DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES insurance_agents(id) ON DELETE SET NULL,
    policy_number VARCHAR(100),
    
    interaction_type VARCHAR(50) NOT NULL, -- e.g., 'CALL', 'CHAT', 'EMAIL'
    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Data references
    raw_data_url VARCHAR(512), 
    cleaned_data_url VARCHAR(512),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_chats (
    job_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
    customer_id VARCHAR(255),
    policy_id VARCHAR(255),
    query TEXT NOT NULL,
    message TEXT,
    status VARCHAR(50) NOT NULL,
    send_time BIGINT NOT NULL
);

-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

-- Customers indexes (email is already uniquely indexed)
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_customers_phone_number ON customers(phone_number);

-- Insurance Agents indexes (email and license_number are already uniquely indexed)
CREATE INDEX idx_agents_name ON insurance_agents(name);
CREATE INDEX idx_agents_agency_name ON insurance_agents(agency_name);

-- Policies indexes (Foreign keys, common filters, & amounts)
CREATE INDEX idx_policies_customer_id ON policies(customer_id);
CREATE INDEX idx_policies_agent_id ON policies(agent_id);
CREATE INDEX idx_policies_status ON policies(status);
CREATE INDEX idx_policies_type ON policies(policy_type);
CREATE INDEX idx_policies_premium ON policies(premium_amount);
CREATE INDEX idx_policies_coverage ON policies(coverage_amount);

-- Customer Interactions indexes (Foreign keys & sorting)
CREATE INDEX idx_interactions_customer_id ON customer_interactions(customer_id);
CREATE INDEX idx_interactions_agent_id ON customer_interactions(agent_id);
CREATE INDEX idx_interactions_date ON customer_interactions(interaction_date);
CREATE INDEX idx_interactions_type ON customer_interactions(interaction_type);
