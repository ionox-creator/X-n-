import io

# Display name replacements (order matters — longer/more specific first)
REPLACEMENTS = [
    # Full product names → Fintel
    ("Capital Precision Engine", "Fintel"),
    ("Capital Auditor Engine", "Fintel"),
    # Product tagline variants
    ("Capital\nPRECISION ENGINE", "Fintel"),  # welcome screen headline
    ("PRECISION ENGINE", "Fintel"),
    # File download names (user-visible)
    ("CPE-Combined-Audit", "Fintel-Combined-Audit"),
    ("CPE-Terminal-Report", "Fintel-Terminal-Report"),
    ("CPE-production-ready.zip", "Fintel-production-ready.zip"),
    # Metadata/SEO
    ("\"Capital Precision Engine\"", "\"Fintel\""),
    # License key prefix in display (if any hardcoded) — keep XXXX placeholder
    # AI system prompt: "You are CPE" and "Capital Precision Engine (CPE)" → "Fintel"
    ('You are "CPE"', 'You are "Fintel"'),
    ('"CPE," "Software," "Platform," or "Service"', '"Fintel," "Software," "Platform," or "Service"'),
    # Footer/version display
    ("Property of Ionox · CPE v1.4", "Property of Ionox · Fintel v1.4"),
    ("CPE v1.4 — Complete Guide", "Fintel v1.4 — Complete Guide"),
    ("CPE v1.4 — SYST", "Fintel v1.4 — SYST"),
    ("CPE Production Build", "Fintel Production Build"),
    # Guide/help text
    ("What is CPE?", "What is Fintel?"),
    ("Understanding the Capital Precision Engine", "Understanding Fintel"),
    ("Get the most out of CPE", "Get the most out of Fintel"),
    # Terms references
    ("the CPE Software", "the Fintel Software"),
    ("the CPE logo", "the Fintel logo"),
    ("CPE is an analytical tool", "Fintel is an analytical tool"),
    ("CPE is designed to perform", "Fintel is designed to perform"),
    ("CPE is built on a zero-data", "Fintel is built on a zero-data"),
    ("CPE does not replace", "Fintel does not replace"),
    ("use of CPE does not", "use of Fintel does not"),
    ("CPE Branding", "Fintel Branding"),
    # Chat/AI references
    ("CPE will respond", "Fintel will respond"),
    ("CPE analyzes and responds", "Fintel analyzes and responds"),
    ("CPE can ", "Fintel can "),
    ("CPE supports ", "Fintel supports "),
    ("CPE's intelligence architecture", "Fintel's intelligence architecture"),
    ("CPE will show the full cap table", "Fintel will show the full cap table"),
    # Title patterns
    ("Capital Precision Engine (CPE)", "Fintel"),
    ("Fintel (CPE)", "Fintel"),  # in case double-applied
    # AI prompt: "The Capital Precision Engine AI" and "powered by"
    ("The Fintel AI", "the Fintel AI"),
    # standalone "(CPE)" remaining in display → remove
    ("(CPE)", ""),
    # "CPE" standalone in user-facing strings (careful: only display contexts)
    # These are safe because they appear in help/guide/chat text
]

# License key hash update (server-side validate-key)
OLD_HASH = "let y=[70,39,24,65,108,168,195,113,31,74,186,210,194,130,84,134,221,123,175,70,71,33,171,177,172,180,30,88,159,225,232,125];"
NEW_HASH = "let y=[111,96,73,189,199,175,211,128,13,28,184,119,136,126,221,212,111,175,91,38,243,92,45,115,145,74,241,135,234,84,166,159];"
# (hash of "FINTEL-X7K9-M2P4-Q8W3" uppercased: 6f6049bdc7afd3800d1cb877887eddd46faf5b26f35c2d73914af187ea54a69f)

def patch(path, label):
    print(f"\n=== {label}: {path} ===")
    try:
        with io.open(path, 'r', encoding='utf-8') as f: s = f.read()
    except Exception as e:
        print(f"  SKIP (cannot read): {e}")
        return
    original = s
    total = 0
    for old, new in REPLACEMENTS:
        cnt = s.count(old)
        if cnt:
            s = s.replace(old, new)
            total += cnt
    if s != original:
        with io.open(path, 'w', encoding='utf-8') as f: f.write(s)
        print(f"  {total} replacements applied")
    else:
        print(f"  no changes")

# Patch client chunk
patch('.next/static/chunks/1aed-jz3ypll2.js', 'client')

# Patch SSR chunk
patch('.next/server/chunks/ssr/[root-of-the-server]__0h1h_or._.js', 'SSR welcome')

# Patch metadata chunk (src_1fcykq0)
patch('.next/server/chunks/ssr/src_1fcykq0._.js', 'metadata')

# Patch AI system prompt chunk
patch('.next/server/chunks/[root-of-the-server]__1-g1ora._.js', 'AI prompt')

# Patch download-report chunk (report HTML templates)
patch('.next/server/chunks/node_modules_next_dist_esm_build_templates_app-route_1a5o629.js', 'report templates')

# Patch license key hash in validate-key
print("\n=== validate-key hash ===")
vk = '.next/server/chunks/[root-of-the-server]__0z2sns6._.js'
with io.open(vk, 'r', encoding='utf-8') as f: s = f.read()
cnt = s.count(OLD_HASH)
if cnt == 1:
    s = s.replace(OLD_HASH, NEW_HASH)
    with io.open(vk, 'w', encoding='utf-8') as f: f.write(s)
    print(f"  hash updated (CPE- → FINTEL- prefix)")
else:
    print(f"  WARNING: hash found {cnt} times, expected 1")

# Patch the license key placeholder (client display)
print("\n=== license key placeholder ===")
client = '.next/static/chunks/1aed-jz3ypll2.js'
with io.open(client, 'r', encoding='utf-8') as f: s = f.read()
# Don't change XXXX-XXXX-XXXX-XXXX format (it's generic)
# But update any "CPE-" prefix shown to users as key format hint
old_hint = 'XXXX-XXXX-XXXX-XXXX'
# Keep placeholder as-is (it's format-agnostic)
print("  placeholder kept as XXXX-XXXX-XXXX-XXXX (format-agnostic)")

print("\n=== DONE ===")
