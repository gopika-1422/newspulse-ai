"""
services/query_builder.py
Expands user queries to improve regional Indian news coverage.
Detects Indian states, cities, and political terms — adds context
so the news APIs find the right articles.
"""

# Map of Indian region keywords → expanded search terms
INDIA_REGION_MAP: dict[str, list[str]] = {
    # South Indian states & UTs
    "tamil nadu":     ["Tamil Nadu", "Chennai", "TN politics"],
    "tamilnadu":      ["Tamil Nadu", "Chennai", "TN politics"],
    "puducherry":     ["Puducherry", "Pondicherry", "Puducherry UT"],
    "pondicherry":    ["Puducherry", "Pondicherry"],
    "kerala":         ["Kerala", "Thiruvananthapuram", "Kochi"],
    "karnataka":      ["Karnataka", "Bengaluru", "Bangalore"],
    "andhra":         ["Andhra Pradesh", "Amaravati", "Vijayawada"],
    "andhra pradesh": ["Andhra Pradesh", "Amaravati", "Vijayawada"],
    "telangana":      ["Telangana", "Hyderabad"],

    # North / West / Central
    "delhi":          ["Delhi", "New Delhi", "AAP BJP Delhi"],
    "mumbai":         ["Mumbai", "Maharashtra"],
    "maharashtra":    ["Maharashtra", "Mumbai", "Pune"],
    "uttar pradesh":  ["Uttar Pradesh", "UP", "Lucknow"],
    "up":             ["Uttar Pradesh", "UP politics"],
    "bihar":          ["Bihar", "Patna"],
    "rajasthan":      ["Rajasthan", "Jaipur"],
    "gujarat":        ["Gujarat", "Ahmedabad", "Surat"],
    "madhya pradesh": ["Madhya Pradesh", "MP", "Bhopal"],
    "punjab":         ["Punjab", "Chandigarh", "Amritsar"],
    "haryana":        ["Haryana", "Gurugram", "Faridabad"],
    "west bengal":    ["West Bengal", "Kolkata", "Mamata"],
    "odisha":         ["Odisha", "Bhubaneswar"],
    "jharkhand":      ["Jharkhand", "Ranchi"],
    "chhattisgarh":   ["Chhattisgarh", "Raipur"],

    # Northeast
    "assam":          ["Assam", "Guwahati"],
    "manipur":        ["Manipur", "Imphal"],
    "meghalaya":      ["Meghalaya", "Shillong"],
    "nagaland":       ["Nagaland", "Kohima"],
    "mizoram":        ["Mizoram", "Aizawl"],
    "tripura":        ["Tripura", "Agartala"],
    "sikkim":         ["Sikkim", "Gangtok"],
    "arunachal":      ["Arunachal Pradesh"],

    # Major cities
    "chennai":        ["Chennai", "Tamil Nadu"],
    "hyderabad":      ["Hyderabad", "Telangana"],
    "bengaluru":      ["Bengaluru", "Bangalore", "Karnataka"],
    "bangalore":      ["Bengaluru", "Bangalore", "Karnataka"],
    "kolkata":        ["Kolkata", "West Bengal"],
    "ahmedabad":      ["Ahmedabad", "Gujarat"],
    "pune":           ["Pune", "Maharashtra"],
    "coimbatore":     ["Coimbatore", "Tamil Nadu"],
    "madurai":        ["Madurai", "Tamil Nadu"],
    "surat":          ["Surat", "Gujarat"],
    "jaipur":         ["Jaipur", "Rajasthan"],
    "lucknow":        ["Lucknow", "Uttar Pradesh"],
    "patna":          ["Patna", "Bihar"],
    "bhopal":         ["Bhopal", "Madhya Pradesh"],
    "nagpur":         ["Nagpur", "Maharashtra"],
    "visakhapatnam":  ["Visakhapatnam", "Vizag", "Andhra Pradesh"],
    "kochi":          ["Kochi", "Cochin", "Kerala"],
    "thiruvananthapuram": ["Thiruvananthapuram", "Trivandrum", "Kerala"],
}

# Political/election terms — append "India" for better results
INDIA_POLITICAL_TERMS = {
    "election", "elections", "vote", "votes", "voting", "bypolls",
    "dmk", "aiadmk", "bjp", "congress", "aap", "tmc", "sp", "bsp",
    "mla", "mp", "cm", "chief minister", "governor", "cabinet",
    "assembly", "lok sabha", "rajya sabha", "constituency",
    "municipal", "panchayat", "corporation", "mayor", "ward",
    "manifesto", "rally", "campaign", "ballot", "polling",
}


def expand_query(raw_query: str) -> str:
    """
    Expand a user query to maximise regional Indian news coverage.

    Examples:
      "Tamil Nadu election"  →  '("Tamil Nadu" OR "Chennai" OR "TN politics") election India'
      "Puducherry"           →  '("Puducherry" OR "Pondicherry" OR "Puducherry UT") India'
      "cricket"              →  'cricket'  (no change)
    """
    lower = raw_query.lower().strip()
    terms: set[str] = set()
    matched_region = False

    for key, expansions in INDIA_REGION_MAP.items():
        if key in lower:
            terms.update(expansions)
            matched_region = True

    if matched_region:
        region_part = " OR ".join(f'"{t}"' for t in sorted(terms))
        # Keep extra words from the query that are not region names
        stop = {"in", "of", "the", "and", "or", "news", "latest"}
        extra_words = [
            w for w in raw_query.split()
            if w.lower() not in stop
            and not any(k in w.lower() for k in INDIA_REGION_MAP)
        ]
        extra = " ".join(extra_words).strip()
        q = f"({region_part})"
        if extra:
            q += f" {extra}"
        q += " India"
        return q

    # Non-region query containing Indian political terms — add "India" context
    if set(lower.split()) & INDIA_POLITICAL_TERMS:
        return f"{raw_query} India"

    return raw_query


def is_india_query(raw_query: str) -> bool:
    """Return True if the query is about Indian regional topics."""
    lower = raw_query.lower()
    if any(k in lower for k in INDIA_REGION_MAP):
        return True
    if set(lower.split()) & INDIA_POLITICAL_TERMS:
        return True
    if "india" in lower:
        return True
    return False
