export const MOCK_CUSTOMERS = {
  "CUST-101": {
    id: "CUST-101",
    name: "Marcus Vance",
    annualPremium: "$2,480",
    tenure: "3.4 yrs",
    sentiment: "+0.68 (Polite/Neutral)",
    churnPropensity: 89,
    history: [
      { month: 'Jan', propensity: 30 },
      { month: 'Feb', propensity: 35 },
      { month: 'Mar', propensity: 38 },
      { month: 'Apr', propensity: 42 },
      { month: 'May', propensity: 50 },
      { month: 'Jun', propensity: 89 }
    ],
    sayVsDo: {
      whatTheySaid: "Everything is fine, just confirming my renewal date and paperless billing.",
      whatTheyDid: "Disabled auto-pay 4 days ago, removed secondary vehicle, payment 16 days past due."
    },
    nextBestAction: {
      offer: "12-Month Rate-Lock (-10% Loyalty Cap)",
      complianceChecks: [
        { name: "Hardship Check", passed: true },
        { name: "Concession Cap 15%", passed: true },
        { name: "Audit Requirement", passed: true }
      ]
    },
    interactions: [
      {
        id: 1,
        time: "2 Days Ago",
        summary: "Customer called to confirm paperless billing. Tone was neutral. Cortex detected no verbal frustration."
      },
      {
        id: 2,
        time: "4 Days Ago",
        summary: "Database Trigger: Customer logged into portal, removed secondary vehicle, and disabled auto-pay."
      }
    ]
  },
  "CUST-102": {
    id: "CUST-102",
    name: "Elena Rostova",
    annualPremium: "$1,850",
    tenure: "5.1 yrs",
    sentiment: "+0.92 (Highly Positive)",
    churnPropensity: 12,
    history: [
      { month: 'Jan', propensity: 18 },
      { month: 'Feb', propensity: 16 },
      { month: 'Mar', propensity: 14 },
      { month: 'Apr', propensity: 15 },
      { month: 'May', propensity: 13 },
      { month: 'Jun', propensity: 12 }
    ],
    sayVsDo: {
      whatTheySaid: "I love the new app update, it's so easy to use.",
      whatTheyDid: "Set up auto-pay for a full year and added a teen driver policy."
    },
    nextBestAction: {
      offer: "Bundle Discount: Home & Auto (-5%)",
      complianceChecks: [
        { name: "Hardship Check", passed: true },
        { name: "Concession Cap 15%", passed: true },
        { name: "Audit Requirement", passed: true }
      ]
    },
    interactions: [
      {
        id: 1,
        time: "1 Week Ago",
        summary: "Added teen driver policy via mobile app without assistance."
      },
      {
        id: 2,
        time: "1 Month Ago",
        summary: "Called to express satisfaction with the claims process for a minor fender bender."
      }
    ]
  }
};
