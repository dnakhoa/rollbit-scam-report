#!/usr/bin/env python3
"""
Rollbit Forensic Investigation Toolkit
=======================================
A comprehensive toolkit for collecting, parsing, analyzing, and visualizing
data related to Rollbit's fund locking and scam behaviors.

Features:
- Forum scraping (Bitcointalk, Trustpilot, Casino Guru, AskGamblers)
- NLP-based complaint classification
- Amount extraction with multi-currency support
- Pattern detection and timeline analysis
- Network analysis of Rollbit staff responses
- Visualization suite (matplotlib/seaborn)
- Export to CSV, JSON, and formatted reports

Usage:
    python rollbit_forensic_toolkit.py --mode analyze
    python rollbit_forensic_toolkit.py --mode scrape --source bitcointalk
    python rollbit_forensic_toolkit.py --mode report
    python rollbit_forensic_toolkit.py --mode visualize
"""

import json
import csv
import re
import os
import sys
import hashlib
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path

# Optional imports with graceful degradation
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('RollbitForensic')

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR
CASES_DB = DATA_DIR / 'cases_database.json'
OUTPUT_DIR = DATA_DIR / 'output'


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ComplaintCase:
    case_id: str
    source: str  # bitcointalk, trustpilot, casino_guru, askgamblers, etc.
    url: str = ''
    thread_title: str = ''
    username_forum: str = ''
    username_rollbit: str = ''
    date_posted: str = ''
    date_resolved: str = ''
    amount_usd: Optional[float] = None
    amount_crypto: str = ''
    amount_currency: str = 'USD'
    category: str = ''
    subcategory: str = ''
    status: str = 'UNRESOLVED'
    details: str = ''
    rollbit_response: str = ''
    evidence: list = field(default_factory=list)
    rollbit_staff_involved: list = field(default_factory=list)
    credibility_score: float = 0.5  # 0-1 scale
    notable: str = ''
    raw_text: str = ''
    fingerprint: str = ''  # dedup hash

    def __post_init__(self):
        if not self.fingerprint:
            dedup_str = f"{self.username_forum}|{self.amount_usd}|{self.date_posted}|{self.source}"
            self.fingerprint = hashlib.md5(dedup_str.encode()).hexdigest()[:12]


# ============================================================================
# AMOUNT EXTRACTION ENGINE
# ============================================================================

class AmountExtractor:
    """Advanced amount extraction from unstructured text with multi-currency support."""

    CURRENCY_PATTERNS = [
        # USD patterns
        (r'\$\s*([\d,]+(?:\.\d{1,2})?)\s*(?:USD|usd|dollars?)?', 'USD', 1.0),
        (r'([\d,]+(?:\.\d{1,2})?)\s*(?:USD|usd|dollars?|bucks)', 'USD', 1.0),
        (r'([\d,]+(?:\.\d{1,2})?)\s*USDT', 'USDT', 1.0),
        (r'([\d,]+(?:\.\d{1,2})?)\s*USDC', 'USDC', 1.0),
        # EUR patterns
        (r'€\s*([\d,]+(?:\.\d{1,2})?)', 'EUR', 1.10),
        (r'([\d,]+(?:\.\d{1,2})?)\s*(?:EUR|euros?)', 'EUR', 1.10),
        # GBP patterns
        (r'£\s*([\d,]+(?:\.\d{1,2})?)', 'GBP', 1.27),
        (r'([\d,]+(?:\.\d{1,2})?)\s*(?:GBP|pounds?)', 'GBP', 1.27),
        # Crypto patterns
        (r'([\d.]+)\s*(?:BTC|bitcoin)', 'BTC', 60000),
        (r'([\d.]+)\s*(?:ETH|ether(?:eum)?)', 'ETH', 3500),
        (r'([\d.]+)\s*(?:SOL|solana)', 'SOL', 150),
        (r'([\d.]+)\s*(?:LTC|litecoin)', 'LTC', 80),
    ]

    CONTEXT_KEYWORDS = {
        'locked': 1.0, 'seized': 1.0, 'stolen': 1.0, 'forfeited': 1.0,
        'confiscated': 1.0, 'blocked': 0.9, 'frozen': 0.9, 'withheld': 0.9,
        'lost': 0.8, 'pending': 0.7, 'withdrawal': 0.8, 'deposit': 0.6,
        'won': 0.7, 'balance': 0.7, 'wagered': 0.3, 'bet': 0.4,
    }

    @classmethod
    def extract_amounts(cls, text: str) -> list:
        """Extract all monetary amounts from text with context relevance scores."""
        results = []
        text_lower = text.lower()
        for pattern, currency, rate in cls.CURRENCY_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                raw = match.group(1).replace(',', '')
                try:
                    value = float(raw)
                except ValueError:
                    continue
                usd_value = value * rate
                # Check surrounding context
                start = max(0, match.start() - 100)
                end = min(len(text_lower), match.end() + 100)
                context = text_lower[start:end]
                relevance = 0.5
                for keyword, weight in cls.CONTEXT_KEYWORDS.items():
                    if keyword in context:
                        relevance = max(relevance, weight)
                results.append({
                    'raw_value': value,
                    'currency': currency,
                    'usd_equivalent': round(usd_value, 2),
                    'context_relevance': relevance,
                    'position': match.start(),
                    'context_snippet': text[start:end].strip()
                })
        results.sort(key=lambda x: (-x['context_relevance'], -x['usd_equivalent']))
        return results

    @classmethod
    def extract_primary_amount(cls, text: str) -> Optional[float]:
        """Get the single most relevant locked/stolen amount from text."""
        amounts = cls.extract_amounts(text)
        for a in amounts:
            if a['context_relevance'] >= 0.7 and a['usd_equivalent'] >= 10:
                return a['usd_equivalent']
        return amounts[0]['usd_equivalent'] if amounts else None


# ============================================================================
# COMPLAINT CLASSIFIER
# ============================================================================

class ComplaintClassifier:
    """Rule-based NLP classifier for categorizing Rollbit complaints."""

    CATEGORY_RULES = {
        'multiple_accounts_accusation': {
            'keywords': ['multiple account', 'multi account', 'duplicate account',
                         'other account', 'linked account', 'ban evasion',
                         'list.*account', 'more than one account'],
            'weight': 1.0,
        },
        'sportsbook_abuse': {
            'keywords': ['sportsbook abuse', 'abusing sport', 'sport.*abuse',
                         'betting abuse', 'bonus abuse'],
            'weight': 0.9,
        },
        'kyc_delay_tactic': {
            'keywords': ['kyc', 'verification', 'level.*verification',
                         'document.*submit', 'compliance.*delay',
                         'pending.*review', 'id.*proof'],
            'weight': 0.7,
        },
        'maintenance_scam': {
            'keywords': ['maintenance', 'scheduled maintenance', 'offline',
                         'platform.*down', 'leverage.*maintenance'],
            'weight': 0.9,
        },
        'restricted_country': {
            'keywords': ['restricted country', 'restricted.*jurisdiction',
                         'geo.*restrict', 'ip.*ban', 'country.*block',
                         'spain', 'belgium', 'uk.*restrict'],
            'weight': 0.8,
        },
        'winning_block': {
            'keywords': ['won.*block', 'winning.*block', 'after.*win.*block',
                         'profitable.*block', 'win.*suspend', 'win.*disable',
                         'big.*win.*lock'],
            'weight': 0.8,
        },
        'futures_manipulation': {
            'keywords': ['futures.*manipul', 'leverage.*scam', 'liquidat',
                         'burst.*price', 'slippage.*manipul', 'funding.*rate'],
            'weight': 0.8,
        },
        'account_closure': {
            'keywords': ['account.*clos', 'account.*disabled', 'account.*banned',
                         'account.*terminat', 'account.*suspend'],
            'weight': 0.6,  # Lower weight - often a symptom, not root cause
        },
    }

    @classmethod
    def classify(cls, text: str) -> list:
        """Return sorted list of (category, confidence) tuples."""
        text_lower = text.lower()
        scores = {}
        for category, config in cls.CATEGORY_RULES.items():
            score = 0
            matches = 0
            for kw in config['keywords']:
                if re.search(kw, text_lower):
                    matches += 1
                    score += config['weight']
            if matches > 0:
                confidence = min(1.0, score / max(len(config['keywords']) * 0.3, 1))
                scores[category] = round(confidence, 3)
        return sorted(scores.items(), key=lambda x: -x[1])

    @classmethod
    def primary_category(cls, text: str) -> str:
        results = cls.classify(text)
        return results[0][0] if results else 'unknown'


# ============================================================================
# CREDIBILITY SCORER
# ============================================================================

class CredibilityScorer:
    """Assess credibility of individual complaint cases."""

    @classmethod
    def score(cls, case: ComplaintCase) -> float:
        score = 0.5  # baseline

        # Evidence provided
        if case.evidence:
            score += min(0.15, len(case.evidence) * 0.05)

        # Blockchain evidence
        if any('transaction' in e.lower() or 'tx' in e.lower() or '0x' in e.lower()
               for e in case.evidence):
            score += 0.1

        # Screenshots / video
        if any('screenshot' in e.lower() or 'video' in e.lower() or 'youtube' in e.lower()
               for e in case.evidence):
            score += 0.05

        # Established forum account
        if case.source == 'bitcointalk':
            score += 0.05  # BTT requires some effort

        # Rollbit actually responded
        if case.rollbit_response:
            score += 0.1  # Confirms engagement

        # Very large amounts less credible without evidence
        if case.amount_usd and case.amount_usd > 50000 and not case.evidence:
            score -= 0.1

        # Resolved cases more credible
        if case.status == 'RESOLVED':
            score += 0.1

        # Multiple corroborating sources
        # (handled at analysis level)

        return round(min(1.0, max(0.0, score)), 2)


# ============================================================================
# FORUM SCRAPERS
# ============================================================================

class BitcointalkScraper:
    """Scraper for Bitcointalk Scam Accusations forum."""

    SEARCH_URL = "https://bitcointalk.org/index.php"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) RollbitForensic/1.0'
    }

    KNOWN_THREADS = [
        {"topic": "5449402", "title": "Rollbit disables account and seizes funds (10.2k)!"},
        {"topic": "5463996", "title": "Rollbit Scam. Cannot Withdraw $30,211"},
        {"topic": "5419674", "title": "Rollbit.com scamming $10,000 USD"},
        {"topic": "5520613", "title": "ROLLBIT MAINTENANCE SCAM"},
        {"topic": "5503600", "title": "Rollbit locked my account with $55k+"},
        {"topic": "5471380", "title": "Rollbit FTX address scam"},
        {"topic": "5489049", "title": "ROLLBIT.COM is a scam. They stole my funds!"},
        {"topic": "5538592", "title": "Rollbit ignore and scam?"},
        {"topic": "5504738", "title": "Rollbit SCAMS restricted players"},
        {"topic": "5489760", "title": "Rollbit locked/pending withdrawals"},
        {"topic": "5412105", "title": "rollbit.com scam"},
        {"topic": "5447471", "title": "Rollbit scam ($350)"},
        {"topic": "5534596", "title": "Scammed by Rollbit"},
        {"topic": "5538532", "title": "Rollbit scam for 400 dollars"},
        {"topic": "5537096", "title": "Rollbit Blocking My funds False Multiple Accounts Claim"},
    ]

    @classmethod
    def scrape_thread(cls, topic_id: str, max_pages: int = 5) -> list:
        """Scrape a Bitcointalk thread and extract complaint data."""
        if not HAS_REQUESTS or not HAS_BS4:
            logger.error("requests and beautifulsoup4 required for scraping")
            return []

        posts = []
        for page in range(max_pages):
            offset = page * 20
            url = f"{cls.SEARCH_URL}?topic={topic_id}.{offset}"
            try:
                resp = requests.get(url, headers=cls.HEADERS, timeout=30)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')

                for post_div in soup.select('div.post'):
                    post_data = cls._parse_post(post_div, topic_id)
                    if post_data:
                        posts.append(post_data)

                # Check if there are more pages
                if not soup.select('a.navPages'):
                    break

            except Exception as e:
                logger.warning(f"Failed to scrape topic {topic_id} page {page}: {e}")
                break

        return posts

    @classmethod
    def _parse_post(cls, post_div, topic_id: str) -> Optional[dict]:
        """Parse a single Bitcointalk post div."""
        try:
            # Extract username
            author_link = post_div.find_previous('td', class_='poster_info')
            username = ''
            if author_link:
                a_tag = author_link.find('a')
                if a_tag:
                    username = a_tag.get_text(strip=True)

            # Extract post text
            inner = post_div.find('div', class_='inner') or post_div
            text = inner.get_text(separator='\n', strip=True)

            # Extract date
            date_elem = post_div.find_previous('td', class_='td_headerandpost')
            date_str = ''
            if date_elem:
                date_div = date_elem.find('div', class_='smalltext')
                if date_div:
                    date_str = date_div.get_text(strip=True)

            # Extract amounts
            amounts = AmountExtractor.extract_amounts(text)

            # Classify
            categories = ComplaintClassifier.classify(text)

            return {
                'topic_id': topic_id,
                'username': username,
                'date': date_str,
                'text': text[:2000],
                'amounts': amounts,
                'categories': categories,
                'has_evidence': bool(re.search(
                    r'(screenshot|proof|evidence|transaction|tx|0x[a-fA-F0-9])',
                    text, re.IGNORECASE
                )),
            }
        except Exception as e:
            logger.warning(f"Failed to parse post: {e}")
            return None

    @classmethod
    def scrape_all_known_threads(cls) -> list:
        """Scrape all known Rollbit complaint threads."""
        all_data = []
        for thread in cls.KNOWN_THREADS:
            logger.info(f"Scraping thread: {thread['title']}")
            posts = cls.scrape_thread(thread['topic'])
            all_data.extend(posts)
        return all_data


class TrustpilotParser:
    """Parser for Trustpilot review pages (expects pre-downloaded HTML)."""

    @classmethod
    def parse_reviews_html(cls, html_content: str) -> list:
        """Parse Trustpilot review page HTML."""
        if not HAS_BS4:
            logger.error("beautifulsoup4 required for parsing")
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        reviews = []

        for review_card in soup.select('[data-review-id]'):
            try:
                # Star rating
                stars_elem = review_card.select_one('[data-star-rating]')
                stars = int(stars_elem['data-star-rating']) if stars_elem else 0

                # Only care about 1-2 star reviews
                if stars > 2:
                    continue

                # Reviewer name
                name_elem = review_card.select_one('[data-consumer-name]')
                name = name_elem.get_text(strip=True) if name_elem else 'Anonymous'

                # Date
                date_elem = review_card.select_one('time')
                date = date_elem.get('datetime', '') if date_elem else ''

                # Review text
                text_elem = review_card.select_one('[data-service-review-text]')
                text = text_elem.get_text(strip=True) if text_elem else ''

                # Extract amounts and classify
                amounts = AmountExtractor.extract_amounts(text)
                categories = ComplaintClassifier.classify(text)

                reviews.append({
                    'reviewer': name,
                    'stars': stars,
                    'date': date[:10] if date else '',
                    'text': text[:1000],
                    'amounts': amounts,
                    'categories': categories,
                    'primary_amount_usd': AmountExtractor.extract_primary_amount(text),
                })
            except Exception as e:
                logger.warning(f"Failed to parse review: {e}")

        return reviews


# ============================================================================
# ANALYSIS ENGINE
# ============================================================================

class ForensicAnalyzer:
    """Core analysis engine for Rollbit complaint data."""

    def __init__(self, cases: list):
        self.cases = cases
        self.df_ready = False

    @classmethod
    def from_json(cls, filepath: str) -> 'ForensicAnalyzer':
        """Load cases from the master JSON database."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        cases = []

        if isinstance(data, dict) and isinstance(data.get('cases'), list):
            raw_cases = [raw for raw in data['cases'] if raw.get('counted_in_totals', True)]
        else:
            raw_cases = []
            for section_key in ['bitcointalk_cases', 'trustpilot_cases',
                                'casino_guru_cases', 'other_forum_cases']:
                source_name = section_key.replace('_cases', '')
                for raw in data.get(section_key, []):
                    normalized = dict(raw)
                    normalized['source'] = raw.get('source', source_name)
                    raw_cases.append(normalized)

        for raw in raw_cases:
            case = ComplaintCase(
                case_id=raw.get('case_id', ''),
                source=raw.get('source', ''),
                url=raw.get('url', raw.get('source_url', raw.get('thread_url', ''))),
                thread_title=raw.get('thread_title', raw.get('title', '')),
                username_forum=raw.get('username_forum', raw.get('reviewer', '')),
                username_rollbit=raw.get('username_rollbit', ''),
                date_posted=raw.get('date_posted', raw.get('post_date', raw.get('date', ''))),
                amount_usd=raw.get('amount_usd'),
                amount_crypto=raw.get('amount_crypto', raw.get('amount_native', '')),
                amount_currency=raw.get('amount_currency', 'USD'),
                category=raw.get('category', ''),
                status=raw.get('status', 'UNRESOLVED'),
                details=raw.get('details', raw.get('summary', '')),
                rollbit_response=raw.get('rollbit_response', ''),
                evidence=raw.get('evidence', []),
                notable=raw.get('notable', raw.get('notes_on_verification', '')),
            )
            case.credibility_score = raw.get('confidence_score', CredibilityScorer.score(case))
            cases.append(case)

        return cls(cases)

    def summary_stats(self) -> dict:
        """Generate comprehensive summary statistics."""
        total = len(self.cases)
        with_amounts = [c for c in self.cases if c.amount_usd]
        amounts = [c.amount_usd for c in with_amounts]

        resolved = sum(1 for c in self.cases if c.status == 'RESOLVED')
        unresolved = sum(1 for c in self.cases if c.status == 'UNRESOLVED')

        # Category breakdown
        cat_counts = Counter(c.category for c in self.cases if c.category)
        cat_amounts = defaultdict(float)
        cat_case_count = defaultdict(int)
        for c in self.cases:
            if c.category and c.amount_usd:
                cat_amounts[c.category] += c.amount_usd
                cat_case_count[c.category] += 1

        # Source breakdown
        source_counts = Counter(c.source for c in self.cases)

        # Timeline (by year-month)
        timeline = defaultdict(lambda: {'count': 0, 'amount': 0})
        for c in self.cases:
            if c.date_posted:
                ym = c.date_posted[:7]  # YYYY-MM
                timeline[ym]['count'] += 1
                if c.amount_usd:
                    timeline[ym]['amount'] += c.amount_usd

        # Staff involvement
        staff_mentions = Counter()
        for c in self.cases:
            text = (c.rollbit_response + ' ' + c.details).lower()
            for staff in ['razer', 'benji', 'smokeylisa', 'lucky', 'jr5', 'm1cha3lm']:
                if staff in text:
                    staff_mentions[staff] += 1

        return {
            'total_cases': total,
            'cases_with_amounts': len(with_amounts),
            'cases_without_amounts': total - len(with_amounts),
            'total_confirmed_usd': round(sum(amounts), 2) if amounts else 0,
            'average_per_case_usd': round(sum(amounts) / len(amounts), 2) if amounts else 0,
            'median_per_case_usd': round(sorted(amounts)[len(amounts) // 2], 2) if amounts else 0,
            'max_single_case_usd': max(amounts) if amounts else 0,
            'min_single_case_usd': min(amounts) if amounts else 0,
            'resolved_count': resolved,
            'unresolved_count': unresolved,
            'resolution_rate': round(resolved / total * 100, 1) if total else 0,
            'category_breakdown': dict(cat_counts.most_common()),
            'category_amounts': dict(sorted(cat_amounts.items(), key=lambda x: -x[1])),
            'category_case_counts': dict(cat_case_count),
            'source_breakdown': dict(source_counts.most_common()),
            'timeline': dict(sorted(timeline.items())),
            'staff_mentions': dict(staff_mentions.most_common()),
            'top_10_cases': [
                {'id': c.case_id, 'amount': c.amount_usd, 'category': c.category,
                 'source': c.source, 'username': c.username_forum}
                for c in sorted(with_amounts, key=lambda x: -x.amount_usd)[:10]
            ],
            'credibility_distribution': {
                'high_0.7+': sum(1 for c in self.cases if c.credibility_score >= 0.7),
                'medium_0.4-0.7': sum(1 for c in self.cases if 0.4 <= c.credibility_score < 0.7),
                'low_<0.4': sum(1 for c in self.cases if c.credibility_score < 0.4),
            }
        }

    def detect_patterns(self) -> dict:
        """Detect behavioral patterns across all cases."""
        patterns = {}

        # Pattern 1: Win-triggered blocks
        win_block_cases = [c for c in self.cases
                           if c.category in ('winning_block', 'sportsbook_abuse')
                           or 'won' in c.details.lower() and 'block' in c.details.lower()]
        patterns['win_triggered_blocks'] = {
            'count': len(win_block_cases),
            'total_amount': sum(c.amount_usd for c in win_block_cases if c.amount_usd),
            'description': 'Accounts blocked immediately after or shortly after winning',
        }

        # Pattern 2: Multiple accounts accusation without evidence
        multi_acc = [c for c in self.cases if c.category == 'multiple_accounts_accusation']
        patterns['false_multiaccounting'] = {
            'count': len(multi_acc),
            'total_amount': sum(c.amount_usd for c in multi_acc if c.amount_usd),
            'description': 'Users accused of having multiple accounts with no evidence provided by Rollbit',
        }

        # Pattern 3: Selective enforcement for restricted countries
        restricted = [c for c in self.cases if c.category == 'restricted_country']
        patterns['selective_enforcement'] = {
            'count': len(restricted),
            'total_amount': sum(c.amount_usd for c in restricted if c.amount_usd),
            'description': 'Deposits accepted from restricted countries, enforcement only triggered at withdrawal time',
        }

        # Pattern 4: KYC escalation loop
        kyc_cases = [c for c in self.cases
                      if c.category == 'kyc_delay_tactic'
                      or 'kyc' in c.details.lower() and 'level' in c.details.lower()]
        patterns['kyc_escalation_loop'] = {
            'count': len(kyc_cases),
            'total_amount': sum(c.amount_usd for c in kyc_cases if c.amount_usd),
            'description': 'Progressive KYC levels (1-5) used to delay withdrawals indefinitely',
        }

        # Pattern 5: Razer's dismissive responses
        razer_cases = [c for c in self.cases if 'razer' in c.rollbit_response.lower()]
        patterns['razer_pattern'] = {
            'count': len(razer_cases),
            'description': 'Admin "Razer" (Jose Llisterri) provides dismissive/mocking responses',
            'examples': [c.rollbit_response[:200] for c in razer_cases if c.rollbit_response][:5],
        }

        # Pattern 6: Silence after initial engagement
        silence_cases = [c for c in self.cases
                          if any(kw in c.details.lower() for kw in
                                 ['stopped responding', 'no response', 'ignored',
                                  'unresponsive', 'silence', 'ceased'])]
        patterns['support_silence'] = {
            'count': len(silence_cases),
            'description': 'Support stops responding after initial engagement, leaving complaint unresolved',
        }

        # Pattern 7: Asymmetric deposit/withdrawal policy
        asymmetric = [c for c in self.cases
                       if 'deposit' in c.details.lower() and
                       any(kw in c.details.lower() for kw in ['block', 'restrict', 'denied', 'refused'])]
        patterns['asymmetric_policy'] = {
            'count': len(asymmetric),
            'description': 'Deposits always accepted freely, but withdrawals systematically blocked',
        }

        return patterns

    def find_duplicates(self) -> list:
        """Detect potential duplicate cases across sources."""
        duplicates = []
        for i, c1 in enumerate(self.cases):
            for c2 in self.cases[i + 1:]:
                score = 0
                # Same amount
                if c1.amount_usd and c2.amount_usd and c1.amount_usd == c2.amount_usd:
                    score += 0.4
                # Similar date
                if c1.date_posted and c2.date_posted:
                    try:
                        d1 = datetime.strptime(c1.date_posted[:10], '%Y-%m-%d')
                        d2 = datetime.strptime(c2.date_posted[:10], '%Y-%m-%d')
                        if abs((d1 - d2).days) <= 30:
                            score += 0.3
                    except ValueError:
                        pass
                # Similar username
                if (c1.username_forum and c2.username_forum and
                        c1.username_forum.lower() == c2.username_forum.lower()):
                    score += 0.5
                # Same category
                if c1.category == c2.category:
                    score += 0.1

                if score >= 0.7:
                    duplicates.append({
                        'case1': c1.case_id,
                        'case2': c2.case_id,
                        'similarity_score': round(score, 2),
                        'reason': f"Amount match: {c1.amount_usd == c2.amount_usd}, "
                                  f"Username: {c1.username_forum} vs {c2.username_forum}"
                    })

        return duplicates

    def export_csv(self, filepath: str):
        """Export all cases to CSV."""
        fieldnames = [
            'case_id', 'source', 'url', 'username_forum', 'date_posted',
            'amount_usd', 'amount_crypto', 'category', 'status',
            'details', 'rollbit_response', 'credibility_score', 'notable'
        ]
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for case in sorted(self.cases,
                               key=lambda x: -(x.amount_usd or 0)):
                row = asdict(case)
                row['evidence'] = '; '.join(case.evidence) if case.evidence else ''
                writer.writerow(row)
        logger.info(f"CSV exported to {filepath}")

    def export_json(self, filepath: str):
        """Export full analysis results to JSON."""
        results = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.summary_stats(),
            'patterns': self.detect_patterns(),
            'duplicates': self.find_duplicates(),
            'all_cases': [asdict(c) for c in self.cases],
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"JSON exported to {filepath}")


# ============================================================================
# VISUALIZATION ENGINE
# ============================================================================

class ForensicVisualizer:
    """Generate investigation visualizations."""

    @staticmethod
    def create_all_charts(analyzer: ForensicAnalyzer, output_dir: str):
        """Generate all visualization charts."""
        if not HAS_MATPLOTLIB:
            logger.error("matplotlib required for visualizations. Install: pip install matplotlib")
            return

        os.makedirs(output_dir, exist_ok=True)
        stats = analyzer.summary_stats()

        ForensicVisualizer._chart_category_breakdown(stats, output_dir)
        ForensicVisualizer._chart_amount_distribution(analyzer, output_dir)
        ForensicVisualizer._chart_timeline(stats, output_dir)
        ForensicVisualizer._chart_source_breakdown(stats, output_dir)
        ForensicVisualizer._chart_top_cases(stats, output_dir)
        ForensicVisualizer._chart_combined_dashboard(analyzer, stats, output_dir)

        logger.info(f"All charts saved to {output_dir}")

    @staticmethod
    def _chart_category_breakdown(stats: dict, output_dir: str):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # Case counts by category
        cats = stats['category_breakdown']
        labels = [k.replace('_', '\n') for k in cats.keys()]
        values = list(cats.values())
        colors = plt.cm.Reds([(v / max(values)) * 0.7 + 0.3 for v in values])

        bars = ax1.barh(labels, values, color=colors, edgecolor='black', linewidth=0.5)
        ax1.set_xlabel('Number of Cases', fontsize=12)
        ax1.set_title('Complaint Categories by Case Count', fontsize=14, fontweight='bold')
        for bar, v in zip(bars, values):
            ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                     str(v), va='center', fontsize=10, fontweight='bold')

        # Amount by category
        cat_amounts = stats['category_amounts']
        if cat_amounts:
            labels2 = [k.replace('_', '\n') for k in cat_amounts.keys()]
            values2 = [v / 1000 for v in cat_amounts.values()]
            colors2 = plt.cm.Oranges([(v / max(values2)) * 0.7 + 0.3 for v in values2])

            bars2 = ax2.barh(labels2, values2, color=colors2, edgecolor='black', linewidth=0.5)
            ax2.set_xlabel('Amount ($ thousands)', fontsize=12)
            ax2.set_title('Confirmed Locked Amounts by Category', fontsize=14, fontweight='bold')
            for bar, v in zip(bars2, values2):
                ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                         f'${v:.1f}K', va='center', fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'category_breakdown.png'), dpi=150, bbox_inches='tight')
        plt.close()

    @staticmethod
    def _chart_amount_distribution(analyzer: ForensicAnalyzer, output_dir: str):
        amounts = [c.amount_usd for c in analyzer.cases if c.amount_usd and c.amount_usd > 0]
        if not amounts:
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # Histogram
        bins = [0, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
        ax1.hist(amounts, bins=bins, color='#e74c3c', edgecolor='black', alpha=0.8)
        ax1.set_xlabel('Amount (USD)', fontsize=12)
        ax1.set_ylabel('Number of Cases', fontsize=12)
        ax1.set_title('Distribution of Locked Amounts', fontsize=14, fontweight='bold')
        ax1.set_xscale('log')

        # Cumulative
        sorted_amounts = sorted(amounts, reverse=True)
        cumulative = []
        running = 0
        for a in sorted_amounts:
            running += a
            cumulative.append(running)

        ax2.plot(range(1, len(cumulative) + 1), [c / 1000 for c in cumulative],
                 'r-o', markersize=4, linewidth=2)
        ax2.set_xlabel('Number of Cases (sorted by amount)', fontsize=12)
        ax2.set_ylabel('Cumulative Amount ($K)', fontsize=12)
        ax2.set_title('Cumulative Locked Funds', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'amount_distribution.png'), dpi=150, bbox_inches='tight')
        plt.close()

    @staticmethod
    def _chart_timeline(stats: dict, output_dir: str):
        timeline = stats['timeline']
        if not timeline:
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

        dates = sorted(timeline.keys())
        counts = [timeline[d]['count'] for d in dates]
        amounts = [timeline[d]['amount'] / 1000 for d in dates]

        ax1.bar(dates, counts, color='#3498db', edgecolor='black', linewidth=0.5)
        ax1.set_ylabel('New Cases', fontsize=12)
        ax1.set_title('Rollbit Complaint Timeline', fontsize=14, fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)

        ax2.bar(dates, amounts, color='#e74c3c', edgecolor='black', linewidth=0.5)
        ax2.set_ylabel('Amount Locked ($K)', fontsize=12)
        ax2.set_xlabel('Month', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'timeline.png'), dpi=150, bbox_inches='tight')
        plt.close()

    @staticmethod
    def _chart_source_breakdown(stats: dict, output_dir: str):
        sources = stats['source_breakdown']
        if not sources:
            return

        fig, ax = plt.subplots(figsize=(10, 8))
        labels = list(sources.keys())
        values = list(sources.values())
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']

        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct='%1.1f%%',
            colors=colors[:len(labels)], startangle=90,
            textprops={'fontsize': 11}
        )
        ax.set_title('Cases by Source Platform', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'source_breakdown.png'), dpi=150, bbox_inches='tight')
        plt.close()

    @staticmethod
    def _chart_top_cases(stats: dict, output_dir: str):
        top = stats['top_10_cases']
        if not top:
            return

        fig, ax = plt.subplots(figsize=(14, 8))
        labels = [f"{c['id']}\n({c['username'][:15]})" for c in top]
        values = [c['amount'] / 1000 for c in top]
        cats = [c['category'].replace('_', '\n') for c in top]
        colors = plt.cm.Reds([(v / max(values)) * 0.6 + 0.4 for v in values])

        bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1],
                       edgecolor='black', linewidth=0.5)
        ax.set_xlabel('Amount Locked ($K)', fontsize=12)
        ax.set_title('Top 10 Largest Confirmed Locked Fund Cases', fontsize=14, fontweight='bold')

        for bar, v, cat in zip(bars, values[::-1], cats[::-1]):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                    f'${v:.1f}K - {cat}', va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'top_cases.png'), dpi=150, bbox_inches='tight')
        plt.close()

    @staticmethod
    def _chart_combined_dashboard(analyzer: ForensicAnalyzer, stats: dict, output_dir: str):
        fig = plt.figure(figsize=(24, 16))
        fig.suptitle('ROLLBIT FORENSIC INVESTIGATION DASHBOARD',
                     fontsize=20, fontweight='bold', color='#c0392b', y=0.98)

        # Summary box
        ax_summary = fig.add_axes([0.02, 0.85, 0.96, 0.10])
        ax_summary.axis('off')
        summary_text = (
            f"Total Cases: {stats['total_cases']}  |  "
            f"Confirmed Locked: ${stats['total_confirmed_usd']:,.0f}  |  "
            f"Cases with Amounts: {stats['cases_with_amounts']}  |  "
            f"Avg per Case: ${stats['average_per_case_usd']:,.0f}  |  "
            f"Max Single Case: ${stats['max_single_case_usd']:,.0f}  |  "
            f"Resolution Rate: {stats['resolution_rate']}%"
        )
        ax_summary.text(0.5, 0.5, summary_text, ha='center', va='center',
                        fontsize=14, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffeaa7', alpha=0.8))

        # Category pie chart
        ax1 = fig.add_subplot(2, 3, 1)
        cats = stats['category_breakdown']
        if cats:
            ax1.pie(cats.values(),
                    labels=[k.replace('_', '\n')[:20] for k in cats.keys()],
                    autopct='%1.0f%%', textprops={'fontsize': 8})
            ax1.set_title('By Category', fontsize=12, fontweight='bold')

        # Amount histogram
        ax2 = fig.add_subplot(2, 3, 2)
        amounts = [c.amount_usd for c in analyzer.cases if c.amount_usd]
        if amounts:
            ax2.hist(amounts, bins=15, color='#e74c3c', edgecolor='black', alpha=0.8)
            ax2.set_title('Amount Distribution', fontsize=12, fontweight='bold')
            ax2.set_xlabel('USD')

        # Source breakdown
        ax3 = fig.add_subplot(2, 3, 3)
        sources = stats['source_breakdown']
        if sources:
            ax3.bar(sources.keys(), sources.values(), color='#3498db')
            ax3.set_title('By Source', fontsize=12, fontweight='bold')
            ax3.tick_params(axis='x', rotation=45)

        # Timeline
        ax4 = fig.add_subplot(2, 3, 4)
        timeline = stats['timeline']
        if timeline:
            dates = sorted(timeline.keys())
            ax4.bar(dates, [timeline[d]['count'] for d in dates], color='#2ecc71')
            ax4.set_title('Cases Over Time', fontsize=12, fontweight='bold')
            ax4.tick_params(axis='x', rotation=45, labelsize=7)

        # Top cases
        ax5 = fig.add_subplot(2, 3, 5)
        top = stats['top_10_cases'][:7]
        if top:
            ax5.barh([c['username'][:12] for c in top][::-1],
                     [c['amount'] / 1000 for c in top][::-1],
                     color='#e74c3c')
            ax5.set_title('Top Cases ($K)', fontsize=12, fontweight='bold')

        # Resolution status
        ax6 = fig.add_subplot(2, 3, 6)
        ax6.pie([stats['resolved_count'], stats['unresolved_count']],
                labels=['Resolved', 'Unresolved'],
                autopct='%1.0f%%',
                colors=['#2ecc71', '#e74c3c'])
        ax6.set_title('Resolution Status', fontsize=12, fontweight='bold')

        plt.savefig(os.path.join(output_dir, 'forensic_dashboard.png'),
                    dpi=150, bbox_inches='tight')
        plt.close()


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generate comprehensive forensic investigation reports."""

    @staticmethod
    def generate_full_report(analyzer: ForensicAnalyzer) -> str:
        stats = analyzer.summary_stats()
        patterns = analyzer.detect_patterns()
        duplicates = analyzer.find_duplicates()

        report = []
        report.append("=" * 80)
        report.append("ROLLBIT FORENSIC INVESTIGATION REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")

        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 40)
        report.append(f"Total documented cases: {stats['total_cases']}")
        report.append(f"Cases with confirmed amounts: {stats['cases_with_amounts']}")
        report.append(f"Total confirmed locked funds: ${stats['total_confirmed_usd']:,.2f}")
        report.append(f"Average per case: ${stats['average_per_case_usd']:,.2f}")
        report.append(f"Median per case: ${stats['median_per_case_usd']:,.2f}")
        report.append(f"Largest single case: ${stats['max_single_case_usd']:,.2f}")
        report.append(f"Resolution rate: {stats['resolution_rate']}%")
        report.append("")

        # Regulatory Context
        report.append("CRITICAL REGULATORY FINDINGS")
        report.append("-" * 40)
        report.append("1. $123 MILLION SEIZED IN UKRAINE (May 2025)")
        report.append("   - Ukrainian court seized crypto assets linked to Bull Gaming N.V. (Rollbit operator)")
        report.append("   - Connected to fraud and money laundering criminal proceedings")
        report.append("   - Bull Gaming confirmed funds 'actually belong to the specified online casino'")
        report.append("")
        report.append("2. LICENSE CONTROVERSY (March 2023)")
        report.append("   - Curacao license removed from website, RLB token dropped 20%")
        report.append("   - Rollbit claimed 'annual renewal' but Curacao sub-licenses are indefinite")
        report.append("   - Anonymous casino owner: Curacao does not disable licenses during renewal")
        report.append("")
        report.append("3. OWNERSHIP (Daniel Dixon & Jose Llisterri)")
        report.append("   - Both British nationals operating from Malta/Curacao")
        report.append("   - Previously ran CSGODiamonds - collapsed after caught rigging games")
        report.append("   - Daniel Dixon ('Lucky') confirmed as owner by competitors")
        report.append("   - Jose Llisterri operates as admin 'Razer' on platform")
        report.append("")
        report.append("4. INFLUENCER FRAUD")
        report.append("   - Fake balances provided to influencers to simulate wins")
        report.append("   - $250,000 RLB offered for 'organic' undisclosed tweets")
        report.append("   - Platform wallets held ~$16M vs ~$75M transferred to Binance")
        report.append("")
        report.append("5. UNDERAGE GAMBLING")
        report.append("   - Documented case: 16-year-old lost $11,000 over 2-3 years")
        report.append("   - No age verification implemented")
        report.append("   - Refund denied")
        report.append("")

        # Category Breakdown
        report.append("COMPLAINT CATEGORIES")
        report.append("-" * 40)
        for cat, count in stats['category_breakdown'].items():
            amount = stats['category_amounts'].get(cat, 0)
            report.append(f"  {cat}: {count} cases, ${amount:,.0f} locked")
        report.append("")

        # Pattern Analysis
        report.append("DETECTED BEHAVIORAL PATTERNS")
        report.append("-" * 40)
        for name, pattern in patterns.items():
            report.append(f"\n  PATTERN: {name.upper()}")
            report.append(f"  Cases: {pattern['count']}")
            if 'total_amount' in pattern:
                report.append(f"  Total amount: ${pattern['total_amount']:,.0f}")
            report.append(f"  Description: {pattern['description']}")
            if 'examples' in pattern:
                for ex in pattern['examples'][:3]:
                    report.append(f"    - \"{ex}\"")
        report.append("")

        # Source Breakdown
        report.append("SOURCE PLATFORMS")
        report.append("-" * 40)
        for source, count in stats['source_breakdown'].items():
            report.append(f"  {source}: {count} cases")
        report.append("")

        # Top 10 Cases
        report.append("TOP 10 LARGEST DOCUMENTED CASES")
        report.append("-" * 40)
        for i, case in enumerate(stats['top_10_cases'], 1):
            report.append(f"  {i}. ${case['amount']:,.0f} - {case['username']} "
                          f"({case['source']}) [{case['category']}]")
        report.append("")

        # Timeline
        report.append("TIMELINE (Monthly)")
        report.append("-" * 40)
        for ym, data in sorted(stats['timeline'].items()):
            bar = "#" * data['count']
            report.append(f"  {ym}: {bar} ({data['count']} cases, ${data['amount']:,.0f})")
        report.append("")

        # Staff Analysis
        report.append("ROLLBIT STAFF INVOLVEMENT")
        report.append("-" * 40)
        for staff, count in stats['staff_mentions'].items():
            report.append(f"  {staff}: mentioned in {count} cases")
        report.append("")

        # Credibility Assessment
        report.append("CREDIBILITY ASSESSMENT")
        report.append("-" * 40)
        cred = stats['credibility_distribution']
        report.append(f"  High credibility (0.7+): {cred['high_0.7+']} cases")
        report.append(f"  Medium credibility (0.4-0.7): {cred['medium_0.4-0.7']} cases")
        report.append(f"  Low credibility (<0.4): {cred['low_<0.4']} cases")
        report.append("")

        # Duplicates
        if duplicates:
            report.append("POTENTIAL DUPLICATE CASES")
            report.append("-" * 40)
            for dup in duplicates:
                report.append(f"  {dup['case1']} <-> {dup['case2']} "
                              f"(similarity: {dup['similarity_score']})")
        report.append("")

        # Detailed Case Listing
        report.append("=" * 80)
        report.append("DETAILED CASE LISTING")
        report.append("=" * 80)
        for case in sorted(analyzer.cases, key=lambda x: -(x.amount_usd or 0)):
            report.append(f"\n--- {case.case_id} ---")
            report.append(f"Source: {case.source}")
            report.append(f"URL: {case.url}")
            report.append(f"User: {case.username_forum}")
            report.append(f"Date: {case.date_posted}")
            report.append(f"Amount: ${case.amount_usd:,.2f}" if case.amount_usd else "Amount: Unknown")
            report.append(f"Category: {case.category}")
            report.append(f"Status: {case.status}")
            report.append(f"Credibility: {case.credibility_score}")
            report.append(f"Details: {case.details[:500]}")
            if case.rollbit_response:
                report.append(f"Rollbit Response: {case.rollbit_response[:300]}")
            if case.evidence:
                report.append(f"Evidence: {'; '.join(case.evidence[:5])}")
            if case.notable:
                report.append(f"NOTABLE: {case.notable}")

        report.append("")
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)

        return '\n'.join(report)


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Rollbit Forensic Investigation Toolkit')
    parser.add_argument('--mode', choices=['analyze', 'scrape', 'report', 'visualize', 'all'],
                        default='all', help='Operation mode')
    parser.add_argument('--source', choices=['bitcointalk', 'trustpilot', 'all'],
                        default='all', help='Scraping source')
    parser.add_argument('--db', default=str(CASES_DB), help='Path to cases database JSON')
    parser.add_argument('--output', default=str(OUTPUT_DIR), help='Output directory')

    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)

    if args.mode in ('analyze', 'all'):
        logger.info("Loading cases database...")
        analyzer = ForensicAnalyzer.from_json(args.db)

        logger.info("Generating summary statistics...")
        stats = analyzer.summary_stats()
        print(json.dumps(stats, indent=2, default=str))

        logger.info("Detecting patterns...")
        patterns = analyzer.detect_patterns()
        print(json.dumps(patterns, indent=2, default=str))

        # Export
        analyzer.export_csv(os.path.join(args.output, 'rollbit_cases.csv'))
        analyzer.export_json(os.path.join(args.output, 'rollbit_analysis.json'))

    if args.mode in ('report', 'all'):
        logger.info("Generating forensic report...")
        analyzer = ForensicAnalyzer.from_json(args.db)
        report = ReportGenerator.generate_full_report(analyzer)

        report_path = os.path.join(args.output, 'ROLLBIT_FORENSIC_REPORT.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to {report_path}")
        print(f"\nReport saved to: {report_path}")

    if args.mode in ('visualize', 'all'):
        if not HAS_MATPLOTLIB:
            logger.error("matplotlib not installed. Run: pip install matplotlib")
        else:
            logger.info("Generating visualizations...")
            analyzer = ForensicAnalyzer.from_json(args.db)
            charts_dir = os.path.join(args.output, 'charts')
            ForensicVisualizer.create_all_charts(analyzer, charts_dir)

    if args.mode in ('scrape',):
        logger.info("Starting scraper...")
        if not HAS_REQUESTS:
            logger.error("requests not installed. Run: pip install requests beautifulsoup4")
            sys.exit(1)
        if args.source in ('bitcointalk', 'all'):
            data = BitcointalkScraper.scrape_all_known_threads()
            scrape_path = os.path.join(args.output, 'bitcointalk_scrape.json')
            with open(scrape_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Scraped {len(data)} posts saved to {scrape_path}")

    logger.info("Done!")


if __name__ == '__main__':
    main()
