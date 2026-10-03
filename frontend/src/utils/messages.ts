export const MESSAGES = {
  loading: [
    "Crunching the numbers...",
    "Reticulating splines...",
    "Waking up the AI...",
    "Pouring virtual coffee...",
    "Gathering customer insights...",
    "Connecting to the mainframe...",
    "Spinning the hamster wheel...",
    "Fetching data from the cloud...",
    "Just a moment, consulting the oracle..."
  ],
  loadingCustomers: [
    "Gathering customer profiles...",
    "Finding the best clients...",
    "Looking up your customers...",
    "Summoning client records..."
  ],
  loadingPolicies: [
    "Searching the policy vault...",
    "Dusting off the policy documents...",
    "Retrieving policy details...",
    "Gathering coverage information..."
  ],
  loadingProfile: [
    "Loading customer profile...",
    "Fetching the 360 degree view...",
    "Piecing together client history...",
    "Loading the complete picture..."
  ],
  emptyPolicies: [
    "No policies found. It's quiet... too quiet.",
    "Zero active policies here. Time to make some calls?",
    "Looks like a blank slate. No policies found.",
    "Nothing to see here! No policies match your search.",
    "Is it just me, or is it empty in here?"
  ],
  emptyCustomers: [
    "No customers found. Did they all go on vacation?",
    "Ghost town! No customers match this search.",
    "Zero customers here. Let's go find some new ones!",
    "It's empty here! Try adjusting your search.",
    "Looks like everyone is hiding!"
  ],
  aiSuggestionsLoading: [
    "Analyzing portfolio for hidden gems...",
    "The AI is deep in thought...",
    "Brewing some smart suggestions...",
    "Consulting the digital oracle...",
    "Looking for cross-sell opportunities...",
    "Scanning for up-sell potential..."
  ],
  aiSuggestionsEmpty: [
    "No suggestions at the moment. Your portfolio is pristine!",
    "The AI took a break. No new insights right now.",
    "Everything looks perfect. No suggestions needed!",
    "All caught up! Check back later for more insights."
  ],
  chatGreeting: [
    "Hello! I am your AI assistant. How can I help you today?",
    "Greetings, human! What's on your mind today?",
    "Hi there! Need help with a policy or customer?",
    "Welcome! I'm ready to assist you. Ask away!",
    "Beep boop! How can I make your day easier?"
  ]
};

export function getRandomMessage(type: keyof typeof MESSAGES): string {
  const messages = MESSAGES[type];
  const randomIndex = Math.floor(Math.random() * messages.length);
  return messages[randomIndex];
}
