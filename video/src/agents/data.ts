// One entry per agent. Copy matches what each tool on the site really does.
export type AgentInfo = {
  id: string;
  name: string;
  role: string;
  tool: string;
  line: string; // one-sentence promise
  input: string; // what you give
  output: string; // what you get
  steps: [string, string, string];
  exampleIn: string;
  exampleOut: string[];
  quip: string; // 3-4 words
  note?: string; // honest limit, shown at the end
};

export const AGENTS: AgentInfo[] = [
  {
    id: 'judge', name: 'Judge SI', role: 'Chief Justice', tool: 'SI Court',
    line: 'Settles petty disagreements with a structured hearing and a shareable ruling.',
    input: 'Both sides of the dispute', output: 'A ruling, a remedy and a certificate',
    steps: ['Each side states its case', 'The court weighs both arguments', 'A ruling and remedy are issued'],
    exampleIn: '"He ate my leftover pizza."  vs  "It looked abandoned."',
    exampleOut: ['Case SI-4821', 'Ruling for Sam', 'Remedy: Alex shall replace the pizza'],
    quip: 'Gavel down. Case closed.',
  },
  {
    id: 'sniffles', name: 'Detective Sniffles', role: 'Rug Sniffer', tool: 'Coin Sniffer',
    line: 'Reviews public data on a Solana coin and flags risks before you buy.',
    input: 'A Solana token address', output: 'A risk score, a verdict and the findings behind it',
    steps: ['Paste the token address', 'Market and on-chain data is checked', 'You get a risk score and findings'],
    exampleIn: 'Token address ending in …pump',
    exampleOut: ['Risk score: 80 / 100', 'HIGH RISK', 'Pool is tiny next to the market cap'],
    quip: 'Hold your nose.',
    note: 'Opinion based on public data. Not financial advice.',
  },
  {
    id: 'chef', name: 'Chef SI', role: 'Head of Fridge Affairs', tool: 'Fridge Roaster',
    line: 'Turns what is already in your fridge into three meals with clear steps.',
    input: 'The ingredients you have', output: 'Three meal ideas with step-by-step recipes',
    steps: ['List what is in your fridge', 'Recipes are matched to your ingredients', 'Cook with clear, numbered steps'],
    exampleIn: 'eggs, rice, spinach, cheese',
    exampleOut: ['Spinach and cheese omelette', 'Egg fried rice', 'Cheesy rice bake'],
    quip: 'Bon appétit, human.',
  },
  {
    id: 'coach', name: 'Coach SI', role: 'Director of Gains', tool: 'Roast-Me Workout',
    line: 'Builds a 7-day bodyweight plan matched to your goal and fitness level.',
    input: 'Your goal and current level', output: 'A 7-day plan with rest days',
    steps: ['Pick your goal', 'Choose your current level', 'Get a 7-day plan with rest days built in'],
    exampleIn: 'Goal: build strength  ·  Level: intermediate',
    exampleOut: ['Day 1 to 3: bodyweight sessions', 'Day 4: Rest day', 'Day 7: Rest day'],
    quip: 'Couch is jealous.',
    note: 'General fitness guidance. Check with a doctor if unsure.',
  },
  {
    id: 'doctor', name: 'Dr. Heartbreak', role: 'Chief of Texts', tool: 'Text-Back Doctor',
    line: 'Explains what a message likely means and drafts your reply in five styles.',
    input: 'The message you received', output: 'A read of the message and five reply drafts',
    steps: ['Paste the message', 'It is analysed for tone and intent', 'Choose a reply: direct, warm, firm, brief or playful'],
    exampleIn: '"Sorry, been super busy lately."',
    exampleOut: ['Likely meaning: low priority right now', 'Direct reply', 'Warm reply  ·  Firm  ·  Brief  ·  Playful'],
    quip: 'Heart intact. Mostly.',
    note: 'A suggestion, not a verdict on anyone.',
  },
  {
    id: 'anchor', name: 'Anchor SI', role: 'Breaking News Desk', tool: 'Breaking News Maker',
    line: 'Turns anything that happened to you into a breaking news card.',
    input: 'A headline and a location', output: 'A news script and a shareable BREAKING card',
    steps: ['Write your headline', 'Add where you are reporting from', 'Download the news card and share it'],
    exampleIn: 'Local man eats last slice of pizza',
    exampleOut: ['LIVE · SI NEWS', 'BREAKING: LOCAL MAN EATS LAST SLICE', 'Reporting from the kitchen'],
    quip: 'More at eleven.',
    note: 'Parody news. Not real news.',
  },
  {
    id: 'professor', name: 'Professor SI', role: 'Keeper of Fine Print', tool: 'Fine-Print Finder',
    line: 'Scans a lease, contract or terms of service and flags the clauses worth a closer look.',
    input: 'The text of a document', output: 'Flagged clauses with plain-language explanations',
    steps: ['Paste the document text', 'It is scanned for risky clauses', 'Each flag is explained in plain words'],
    exampleIn: 'Lease: "shall automatically renew for successive terms…"',
    exampleOut: ['Auto-renewal · Watch', 'No refunds · Watch', 'Overall attention level: HIGH'],
    quip: 'Read it twice.',
    note: 'A keyword scan, not legal advice. Your text stays in your browser.',
  },
  {
    id: 'dj', name: 'DJ SI', role: 'Minister of Bars', tool: 'Rap Battle Roast',
    line: 'Writes eight bars about any person, team or thing, as a hype track or a light roast.',
    input: 'A name or a topic, plus a style', output: 'Eight bars, ready to share',
    steps: ['Enter who or what the bars are about', 'Choose hype track or light roast', 'Get eight bars to share'],
    exampleIn: 'Mondays  ·  Light roast',
    exampleOut: ['Eight bars, rhymed in couplets', 'Shareable lyric card'],
    quip: 'Mic dropped. Politely.',
  },
  {
    id: 'banker', name: 'Banker SI', role: 'Treasurer', tool: 'Can I Afford It?',
    line: 'Runs the numbers on a purchase and gives a clear affordability verdict.',
    input: 'Price, monthly free money and savings', output: 'A verdict and how long it would take',
    steps: ['Enter the price', 'Add your monthly free money and savings', 'Get a clear verdict and timeline'],
    exampleIn: '$600 purchase  ·  $300 free per month',
    exampleOut: ['ABOUT 2 MONTHS', 'Set aside your free money for 2 months', 'An automatic transfer helps'],
    quip: 'Wallet has opinions.',
    note: 'A rough guide, not financial advice.',
  },
  {
    id: 'astronaut', name: 'Astronaut SI', role: 'Lost in Space', tool: 'Space Horoscope',
    line: 'A cosmic forecast for your sign, delivered from somewhere near the moon.',
    input: 'Your sign and an optional topic', output: 'A forecast for the day',
    steps: ['Pick your sign', 'Add a topic if you like', 'Read your forecast'],
    exampleIn: 'Leo  ·  Topic: work',
    exampleOut: ['Forecast for Leo', 'Lucky number and mood', 'Cosmic Wi-Fi: occasionally unstable.'],
    quip: 'Houston, vibe problem.',
    note: 'For entertainment only.',
  },
];
