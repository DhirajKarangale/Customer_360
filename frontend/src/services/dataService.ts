// Mock data service simulating Snowflake SQL / Cortex API responses
export const fetchCustomerData = async (customerId) => {
  // Simulate network delay to mimic DB connection
  await new Promise(resolve => setTimeout(resolve, 800));

  const mockDb = {
    'CUST-101': {
      id: 'CUST-101',
      name: 'Marcus Vance',
      annualPremium: 2480.00,
      tenureYears: 3.4,
      cortexSentiment: '+0.68',
      cortexSummary: '"Information gathering, no explicit churn threat."',
      churnPropensity: 89,
      churnRiskLevel: 'Critical',
      churnSubtext: 'Stealth Flight Risk',
      sayVsDo: {
        said: "Hi, I was just calling to politely inquire about my upcoming renewal dates. Everything has been great so far!",
        did: ["Disabled auto-pay on main policy", "Removed secondary vehicle from account", "Currently 16 days past due"]
      },
      nba: {
        title: "12-Month Rate-Lock Offer",
        description: "Waive late fees and lock current premium for 12 months in exchange for re-enabling auto-pay."
      }
    },
    'CUST-102': {
      id: 'CUST-102',
      name: 'Elena Rostova',
      annualPremium: 1850.00,
      tenureYears: 5.1,
      cortexSentiment: '+0.20',
      cortexSummary: '"Routine account maintenance. Neutral sentiment."',
      churnPropensity: 45,
      churnRiskLevel: 'Moderate',
      churnSubtext: 'Competitor Shopping',
      sayVsDo: {
        said: "I just need to update my billing address since we moved last week.",
        did: ["Logged in 4 times this week", "Viewed cancellation policy page for 3 minutes"]
      },
      nba: {
        title: "Loyalty Discount Review",
        description: "Offer 5% multi-policy discount to prevent shopping around and acknowledge the move."
      }
    }
  };

  // If customerId is just "CUST-101 (Marcus Vance)", extract the ID
  const parsedId = customerId.split(' ')[0];
  
  return mockDb[parsedId] || mockDb['CUST-101'];
};
