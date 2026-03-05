/**
 * Rollbit Forum Scraper & Parser
 * ================================
 * Advanced JavaScript toolkit for extracting, parsing, and analyzing
 * Rollbit complaint data from multiple forum sources.
 *
 * Can run in:
 * - Node.js with cheerio (npm install cheerio node-fetch)
 * - Browser console (for Trustpilot/forum pages)
 *
 * Usage:
 *   node rollbit_forum_scraper.js --source bitcointalk --output ./data
 *   node rollbit_forum_scraper.js --source trustpilot --pages 10
 *   node rollbit_forum_scraper.js --analyze ./cases_database.json
 */

const fs = typeof require !== 'undefined' ? require('fs') : null;
const path = typeof require !== 'undefined' ? require('path') : null;

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  bitcointalk: {
    baseUrl: 'https://bitcointalk.org/index.php',
    threadsPerPage: 20,
    knownThreads: [
      { topic: '5449402', title: 'Rollbit disables account and seizes funds (10.2k)!' },
      { topic: '5463996', title: 'Rollbit Scam. Cannot Withdraw $30,211' },
      { topic: '5419674', title: 'Rollbit.com scamming $10,000 USD' },
      { topic: '5520613', title: 'ROLLBIT MAINTENANCE SCAM' },
      { topic: '5503600', title: 'Rollbit locked my account with $55k+' },
      { topic: '5471380', title: 'Rollbit FTX address scam' },
      { topic: '5489049', title: 'ROLLBIT.COM is a scam' },
      { topic: '5538592', title: 'Rollbit ignore and scam?' },
      { topic: '5504738', title: 'Rollbit SCAMS restricted players' },
      { topic: '5489760', title: 'Rollbit locked/pending withdrawals' },
      { topic: '5412105', title: 'rollbit.com scam' },
      { topic: '5447471', title: 'Rollbit scam ($350)' },
      { topic: '5534596', title: 'Scammed by Rollbit' },
      { topic: '5538532', title: 'Rollbit scam for 400 dollars' },
      { topic: '5537096', title: 'Rollbit Blocking My funds' },
    ],
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) RollbitForensic/1.0'
    }
  },
  trustpilot: {
    baseUrl: 'https://www.trustpilot.com/review/www.rollbit.com',
    maxPages: 50,
    rateLimitMs: 2000,
  },
  casinoGuru: {
    searchUrl: 'https://casino.guru/complaints',
    casino: 'rollbit-casino',
  },
};

// ============================================================================
// AMOUNT EXTRACTION ENGINE
// ============================================================================

class AmountExtractor {
  static PATTERNS = [
    // USD
    { regex: /\$\s*([\d,]+(?:\.\d{1,2})?)\s*(?:USD|usd|dollars?)?/gi, currency: 'USD', rate: 1 },
    { regex: /([\d,]+(?:\.\d{1,2})?)\s*(?:USD|USDT|USDC|dollars?|bucks)/gi, currency: 'USD', rate: 1 },
    // EUR
    { regex: /€\s*([\d,]+(?:\.\d{1,2})?)/gi, currency: 'EUR', rate: 1.10 },
    { regex: /([\d,]+(?:\.\d{1,2})?)\s*(?:EUR|euros?)/gi, currency: 'EUR', rate: 1.10 },
    // GBP
    { regex: /£\s*([\d,]+(?:\.\d{1,2})?)/gi, currency: 'GBP', rate: 1.27 },
    // Crypto
    { regex: /([\d.]+)\s*(?:BTC|bitcoin)/gi, currency: 'BTC', rate: 60000 },
    { regex: /([\d.]+)\s*(?:ETH|ether(?:eum)?)/gi, currency: 'ETH', rate: 3500 },
    { regex: /([\d.]+)\s*(?:SOL|solana)/gi, currency: 'SOL', rate: 150 },
  ];

  static CONTEXT_WORDS = {
    locked: 1.0, seized: 1.0, stolen: 1.0, forfeited: 1.0, confiscated: 1.0,
    blocked: 0.9, frozen: 0.9, withheld: 0.9, lost: 0.8, pending: 0.7,
    withdrawal: 0.8, deposit: 0.6, won: 0.7, balance: 0.7,
    wagered: 0.3, bet: 0.4,
  };

  static extractAll(text) {
    const results = [];
    const textLower = text.toLowerCase();

    for (const { regex, currency, rate } of this.PATTERNS) {
      regex.lastIndex = 0;
      let match;
      while ((match = regex.exec(text)) !== null) {
        const rawValue = parseFloat(match[1].replace(/,/g, ''));
        if (isNaN(rawValue) || rawValue <= 0) continue;

        const usdEquiv = rawValue * rate;
        const start = Math.max(0, match.index - 80);
        const end = Math.min(textLower.length, match.index + match[0].length + 80);
        const context = textLower.slice(start, end);

        let relevance = 0.5;
        for (const [word, weight] of Object.entries(this.CONTEXT_WORDS)) {
          if (context.includes(word)) relevance = Math.max(relevance, weight);
        }

        results.push({
          rawValue,
          currency,
          usdEquivalent: Math.round(usdEquiv * 100) / 100,
          relevance,
          position: match.index,
          contextSnippet: text.slice(start, end).trim(),
        });
      }
    }

    results.sort((a, b) => b.relevance - a.relevance || b.usdEquivalent - a.usdEquivalent);
    return results;
  }

  static extractPrimary(text) {
    const amounts = this.extractAll(text);
    for (const a of amounts) {
      if (a.relevance >= 0.7 && a.usdEquivalent >= 10) return a.usdEquivalent;
    }
    return amounts.length > 0 ? amounts[0].usdEquivalent : null;
  }
}

// ============================================================================
// COMPLAINT CLASSIFIER
// ============================================================================

class ComplaintClassifier {
  static RULES = {
    multiple_accounts_accusation: {
      patterns: [
        /multiple\s*account/i, /multi[\s-]*account/i, /duplicate\s*account/i,
        /other\s*account/i, /linked\s*account/i, /ban\s*evasion/i,
        /list.*account/i, /more\s*than\s*one\s*account/i,
      ],
      weight: 1.0,
    },
    sportsbook_abuse: {
      patterns: [
        /sportsbook\s*abuse/i, /abusing\s*sport/i, /sport.*abuse/i,
        /betting\s*abuse/i, /bonus\s*abuse/i,
      ],
      weight: 0.9,
    },
    kyc_delay_tactic: {
      patterns: [
        /kyc/i, /verification/i, /level\s*\d+\s*verification/i,
        /compliance.*delay/i, /pending.*review/i,
      ],
      weight: 0.7,
    },
    maintenance_scam: {
      patterns: [
        /maintenance/i, /scheduled\s*maintenance/i,
        /platform.*down/i, /leverage.*maintenance/i,
      ],
      weight: 0.9,
    },
    restricted_country: {
      patterns: [
        /restricted\s*country/i, /restricted.*jurisdiction/i,
        /geo.*restrict/i, /ip.*ban/i,
      ],
      weight: 0.8,
    },
    winning_block: {
      patterns: [
        /won.*block/i, /winning.*block/i, /after.*win.*block/i,
        /profitable.*block/i, /win.*suspend/i, /win.*disable/i,
      ],
      weight: 0.8,
    },
    futures_manipulation: {
      patterns: [
        /futures.*manipul/i, /leverage.*scam/i, /liquidat/i,
        /burst.*price/i, /slippage/i,
      ],
      weight: 0.8,
    },
    account_closure: {
      patterns: [
        /account.*clos/i, /account.*disabled/i, /account.*banned/i,
        /account.*terminat/i, /account.*suspend/i,
      ],
      weight: 0.6,
    },
  };

  static classify(text) {
    const scores = {};
    for (const [category, config] of Object.entries(this.RULES)) {
      let matches = 0;
      for (const pattern of config.patterns) {
        if (pattern.test(text)) matches++;
      }
      if (matches > 0) {
        const confidence = Math.min(1.0, (matches * config.weight) / (config.patterns.length * 0.3));
        scores[category] = Math.round(confidence * 1000) / 1000;
      }
    }
    return Object.entries(scores).sort((a, b) => b[1] - a[1]);
  }

  static primaryCategory(text) {
    const results = this.classify(text);
    return results.length > 0 ? results[0][0] : 'unknown';
  }
}

// ============================================================================
// BITCOINTALK PARSER
// ============================================================================

class BitcointalkParser {
  /**
   * Parse a Bitcointalk thread HTML page.
   * Works with cheerio (Node.js) or native DOM (browser).
   */
  static parseThreadPage(html, topicId) {
    let $;
    const isBrowser = typeof document !== 'undefined' && typeof window !== 'undefined';

    if (isBrowser) {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      return this._parseDOMNative(doc, topicId);
    } else {
      try {
        const cheerio = require('cheerio');
        $ = cheerio.load(html);
        return this._parseCheerio($, topicId);
      } catch {
        console.error('Install cheerio: npm install cheerio');
        return [];
      }
    }
  }

  static _parseCheerio($, topicId) {
    const posts = [];

    $('div.post').each((_, postEl) => {
      const $post = $(postEl);
      const text = $post.text().trim();
      const posterId = $post.closest('tr').find('td.poster_info a').first().text().trim();

      // Date extraction
      const headerTd = $post.closest('td.td_headerandpost');
      const dateText = headerTd ? headerTd.find('div.smalltext').first().text().trim() : '';

      const amounts = AmountExtractor.extractAll(text);
      const categories = ComplaintClassifier.classify(text);

      // Detect Rollbit staff
      const staffMentions = [];
      for (const name of ['Razer', 'Benji', 'SmokeyLisa', 'Lucky', 'JR5', 'M1cha3lM']) {
        if (text.includes(name)) staffMentions.push(name);
      }

      // Evidence detection
      const hasEvidence = /screenshot|proof|evidence|transaction|tx\s|0x[a-fA-F0-9]{10}/i.test(text);
      const hasBlockchainProof = /0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}/i.test(text);

      posts.push({
        topicId,
        username: posterId,
        date: dateText,
        text: text.substring(0, 2000),
        amounts,
        categories,
        staffMentions,
        hasEvidence,
        hasBlockchainProof,
        isOP: posts.length === 0, // first post is OP
      });
    });

    return posts;
  }

  static _parseDOMNative(doc, topicId) {
    const posts = [];
    const postDivs = doc.querySelectorAll('div.post');

    postDivs.forEach((postEl) => {
      const text = postEl.textContent.trim();
      const posterLink = postEl.closest('tr')?.querySelector('td.poster_info a');
      const username = posterLink ? posterLink.textContent.trim() : 'Unknown';

      const amounts = AmountExtractor.extractAll(text);
      const categories = ComplaintClassifier.classify(text);

      posts.push({
        topicId,
        username,
        text: text.substring(0, 2000),
        amounts,
        categories,
        isOP: posts.length === 0,
      });
    });

    return posts;
  }
}

// ============================================================================
// TRUSTPILOT PARSER
// ============================================================================

class TrustpilotParser {
  /**
   * Parse Trustpilot review page.
   * Best used in browser console on the actual Trustpilot page.
   */
  static parseCurrentPage() {
    if (typeof document === 'undefined') {
      console.error('This method is designed to run in a browser');
      return [];
    }

    const reviews = [];
    const reviewCards = document.querySelectorAll('[data-review-id], article');

    reviewCards.forEach(card => {
      try {
        // Star rating
        const starsEl = card.querySelector('[data-star-rating], .star-rating');
        const stars = starsEl
          ? parseInt(starsEl.getAttribute('data-star-rating') || starsEl.textContent)
          : 0;

        // Only complaints (1-2 stars)
        if (stars > 2) return;

        // Reviewer name
        const nameEl = card.querySelector('[data-consumer-name], .consumer-information__name');
        const name = nameEl ? nameEl.textContent.trim() : 'Anonymous';

        // Date
        const timeEl = card.querySelector('time');
        const date = timeEl ? timeEl.getAttribute('datetime') || timeEl.textContent : '';

        // Review text
        const textEl = card.querySelector('[data-service-review-text], .review-content__text');
        const text = textEl ? textEl.textContent.trim() : '';

        // Title
        const titleEl = card.querySelector('[data-service-review-title], .review-content__title');
        const title = titleEl ? titleEl.textContent.trim() : '';

        const fullText = `${title} ${text}`;
        const amounts = AmountExtractor.extractAll(fullText);
        const categories = ComplaintClassifier.classify(fullText);

        reviews.push({
          reviewer: name,
          stars,
          date: date.substring(0, 10),
          title,
          text: text.substring(0, 1000),
          amounts,
          primaryAmountUsd: AmountExtractor.extractPrimary(fullText),
          categories,
          primaryCategory: ComplaintClassifier.primaryCategory(fullText),
        });
      } catch (e) {
        console.warn('Failed to parse review card:', e);
      }
    });

    return reviews;
  }

  /**
   * Auto-scroll and collect all reviews across pages.
   * Run this in browser console on Trustpilot.
   */
  static async collectAllPages(maxPages = 50) {
    const allReviews = [];

    for (let page = 1; page <= maxPages; page++) {
      console.log(`Fetching page ${page}...`);
      window.location.href = `https://www.trustpilot.com/review/www.rollbit.com?page=${page}&sort=recency`;

      // Wait for page load
      await new Promise(r => setTimeout(r, 3000));

      const pageReviews = this.parseCurrentPage();
      allReviews.push(...pageReviews);
      console.log(`Page ${page}: ${pageReviews.length} complaints found (total: ${allReviews.length})`);

      if (pageReviews.length === 0) break;
    }

    return allReviews;
  }
}

// ============================================================================
// ANALYSIS ENGINE
// ============================================================================

class ForensicAnalyzer {
  constructor(cases) {
    this.cases = cases;
  }

  static fromJSON(jsonPath) {
    const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
    const cases = [];

    for (const section of ['bitcointalk_cases', 'trustpilot_cases', 'casino_guru_cases', 'other_forum_cases']) {
      for (const raw of (data[section] || [])) {
        cases.push({
          caseId: raw.case_id,
          source: raw.source || section.replace('_cases', ''),
          url: raw.url || raw.thread_url || '',
          username: raw.username_forum || raw.reviewer || '',
          date: raw.date_posted || raw.date || '',
          amountUsd: raw.amount_usd,
          category: raw.category || '',
          status: raw.status || 'UNRESOLVED',
          details: raw.details || '',
          rollbitResponse: raw.rollbit_response || '',
          evidence: raw.evidence || [],
          notable: raw.notable || '',
        });
      }
    }

    return new ForensicAnalyzer(cases);
  }

  summarize() {
    const withAmounts = this.cases.filter(c => c.amountUsd != null && c.amountUsd > 0);
    const amounts = withAmounts.map(c => c.amountUsd);

    const categoryMap = {};
    const categoryAmounts = {};
    for (const c of this.cases) {
      if (c.category) {
        categoryMap[c.category] = (categoryMap[c.category] || 0) + 1;
        if (c.amountUsd) {
          categoryAmounts[c.category] = (categoryAmounts[c.category] || 0) + c.amountUsd;
        }
      }
    }

    const sourceMap = {};
    for (const c of this.cases) {
      const src = c.source || 'unknown';
      sourceMap[src] = (sourceMap[src] || 0) + 1;
    }

    const timeline = {};
    for (const c of this.cases) {
      if (c.date) {
        const ym = c.date.substring(0, 7);
        if (!timeline[ym]) timeline[ym] = { count: 0, amount: 0 };
        timeline[ym].count++;
        if (c.amountUsd) timeline[ym].amount += c.amountUsd;
      }
    }

    return {
      totalCases: this.cases.length,
      casesWithAmounts: withAmounts.length,
      totalConfirmedUsd: amounts.reduce((a, b) => a + b, 0),
      averagePerCase: amounts.length ? amounts.reduce((a, b) => a + b, 0) / amounts.length : 0,
      maxSingleCase: amounts.length ? Math.max(...amounts) : 0,
      resolvedCount: this.cases.filter(c => c.status === 'RESOLVED').length,
      unresolvedCount: this.cases.filter(c => c.status !== 'RESOLVED').length,
      categoryBreakdown: categoryMap,
      categoryAmounts,
      sourceBreakdown: sourceMap,
      timeline: Object.fromEntries(Object.entries(timeline).sort()),
      top10: withAmounts
        .sort((a, b) => b.amountUsd - a.amountUsd)
        .slice(0, 10)
        .map(c => ({ id: c.caseId, amount: c.amountUsd, user: c.username, category: c.category })),
    };
  }

  exportCSV() {
    const headers = ['case_id', 'source', 'url', 'username', 'date', 'amount_usd', 'category', 'status', 'details'];
    const rows = [headers.join(',')];

    for (const c of this.cases.sort((a, b) => (b.amountUsd || 0) - (a.amountUsd || 0))) {
      const row = [
        c.caseId, c.source, c.url, c.username, c.date,
        c.amountUsd || '', c.category, c.status,
        `"${(c.details || '').replace(/"/g, '""').substring(0, 500)}"`,
      ];
      rows.push(row.join(','));
    }

    return rows.join('\n');
  }

  /**
   * Generate a detailed text report.
   */
  generateReport() {
    const stats = this.summarize();
    const lines = [];

    lines.push('='.repeat(80));
    lines.push('ROLLBIT FORENSIC INVESTIGATION - JAVASCRIPT ANALYSIS');
    lines.push(`Generated: ${new Date().toISOString()}`);
    lines.push('='.repeat(80));
    lines.push('');
    lines.push(`Total Cases: ${stats.totalCases}`);
    lines.push(`Confirmed Locked Funds: $${stats.totalConfirmedUsd.toLocaleString()}`);
    lines.push(`Average per Case: $${Math.round(stats.averagePerCase).toLocaleString()}`);
    lines.push(`Max Single Case: $${stats.maxSingleCase.toLocaleString()}`);
    lines.push(`Resolution Rate: ${Math.round(stats.resolvedCount / stats.totalCases * 100)}%`);
    lines.push('');

    lines.push('CATEGORY BREAKDOWN:');
    for (const [cat, count] of Object.entries(stats.categoryBreakdown).sort((a, b) => b[1] - a[1])) {
      const amount = stats.categoryAmounts[cat] || 0;
      lines.push(`  ${cat}: ${count} cases, $${amount.toLocaleString()}`);
    }
    lines.push('');

    lines.push('TOP 10 CASES:');
    stats.top10.forEach((c, i) => {
      lines.push(`  ${i + 1}. $${c.amount.toLocaleString()} - ${c.user} [${c.category}]`);
    });

    return lines.join('\n');
  }
}

// ============================================================================
// BROWSER CONSOLE HELPER
// ============================================================================

/**
 * Quick extraction helper - paste this in browser console on any Rollbit complaint page.
 * Usage: extractRollbitComplaints()
 */
function extractRollbitComplaints() {
  const text = document.body.innerText;
  const amounts = AmountExtractor.extractAll(text);
  const categories = ComplaintClassifier.classify(text);

  console.log('=== Rollbit Complaint Extraction ===');
  console.log('Amounts found:', amounts);
  console.log('Categories:', categories);
  console.log('Primary amount:', AmountExtractor.extractPrimary(text));
  console.log('Primary category:', ComplaintClassifier.primaryCategory(text));

  return { amounts, categories, text: text.substring(0, 5000) };
}

// ============================================================================
// NODE.JS CLI
// ============================================================================

if (typeof require !== 'undefined' && require.main === module) {
  const args = process.argv.slice(2);

  if (args.includes('--analyze')) {
    const jsonPath = args[args.indexOf('--analyze') + 1] || './cases_database.json';
    console.log(`Analyzing: ${jsonPath}`);

    const analyzer = ForensicAnalyzer.fromJSON(jsonPath);
    const summary = analyzer.summarize();
    console.log(JSON.stringify(summary, null, 2));

    // Export CSV
    const csvData = analyzer.exportCSV();
    fs.writeFileSync('./rollbit_cases_js.csv', csvData);
    console.log('CSV exported to rollbit_cases_js.csv');

    // Generate report
    const report = analyzer.generateReport();
    fs.writeFileSync('./rollbit_report_js.txt', report);
    console.log('Report exported to rollbit_report_js.txt');
  } else {
    console.log('Rollbit Forum Scraper & Parser');
    console.log('Usage:');
    console.log('  node rollbit_forum_scraper.js --analyze ./cases_database.json');
    console.log('');
    console.log('For browser usage:');
    console.log('  Copy this file content into browser console on Trustpilot/Bitcointalk pages');
    console.log('  Then run: extractRollbitComplaints() or TrustpilotParser.parseCurrentPage()');
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    AmountExtractor,
    ComplaintClassifier,
    BitcointalkParser,
    TrustpilotParser,
    ForensicAnalyzer,
    extractRollbitComplaints,
  };
}
