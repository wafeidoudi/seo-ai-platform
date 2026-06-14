# backend/app/services/scoring.py
from typing import Dict, Any, List, Tuple


def score_technical(raw: Dict[str, Any]) -> Tuple[int, List[Dict]]:
    """
    Calculer le score Technical SEO (0-100)
    
    Returns:
        tuple: (score, issues)
    """
    score = 0
    issues = []
    
    tech = raw.get("technical", {})
    performance = raw.get("performance", {})
    
    # Robots.txt (15 points)
    if tech.get("has_robots_txt"):
        score += 15
    else:
        issues.append({
            "id": "missing-robots",
            "icon": "fa-robot",
            "title": "Missing robots.txt",
            "description": "The robots.txt file helps search engines crawl your site efficiently.",
            "impact": "Medium - May affect crawl efficiency",
            "solution": "Create a robots.txt file at the root of your website",
            "priority": "medium"
        })
    
    # Sitemap (15 points)
    if tech.get("has_sitemap"):
        score += 15
    else:
        issues.append({
            "id": "missing-sitemap",
            "icon": "fa-sitemap",
            "title": "Missing sitemap.xml",
            "description": "Sitemap helps search engines discover all your pages.",
            "impact": "Medium - Some pages may not be indexed",
            "solution": "Create and submit a sitemap.xml to search engines",
            "priority": "medium"
        })
    
    # HTTPS (20 points)
    if tech.get("is_https"):
        score += 20
    else:
        issues.append({
            "id": "no-https",
            "icon": "fa-lock",
            "title": "Site Not Using HTTPS",
            "description": "Non-HTTPS sites are flagged as insecure by browsers.",
            "impact": "Critical - Security warning + ranking penalty",
            "solution": "Install an SSL certificate and redirect HTTP to HTTPS",
            "priority": "critical"
        })
    
    # Viewport (15 points)
    if tech.get("has_viewport"):
        score += 15
    else:
        issues.append({
            "id": "no-viewport",
            "icon": "fa-mobile-screen",
            "title": "Missing Viewport Meta Tag",
            "description": "Without viewport tag, mobile rendering may be incorrect.",
            "impact": "High - Poor mobile experience",
            "solution": "Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            "priority": "high"
        })
    
    # Load Time (20 points)
    load_time = tech.get("load_time_ms", 0)
    if load_time < 2000:
        score += 20
    elif load_time < 4000:
        score += 15
    elif load_time < 6000:
        score += 10
    else:
        score += 5
        issues.append({
            "id": "slow-load",
            "icon": "fa-gauge-high",
            "title": "Slow Page Load Time",
            "description": f"Page loads in {load_time/1000:.1f}s, above recommended 3s threshold.",
            "impact": "High - Higher bounce rate, lower rankings",
            "solution": "Optimize images, enable caching, minify CSS/JS",
            "priority": "high"
        })
    
    # Structured Data (15 points)
    if tech.get("has_structured_data"):
        score += 15
    else:
        issues.append({
            "id": "no-structured-data",
            "icon": "fa-code",
            "title": "No Structured Data Detected",
            "description": "Schema.org markup helps search engines understand content.",
            "impact": "Low - Missed rich snippets opportunity",
            "solution": "Add JSON-LD structured data for your content type",
            "priority": "low"
        })
    
    return min(score, 100), issues


def score_content(raw: Dict[str, Any]) -> Tuple[int, List[Dict]]:
    """
    Calculer le score Content SEO (0-100)
    """
    score = 0
    issues = []
    
    meta_tags = raw.get("meta_tags", {})
    headings = raw.get("headings", {})
    
    # Title Tag (25 points)
    title = meta_tags.get("title")
    title_length = meta_tags.get("title_length", 0)
    
    if title:
        if 30 <= title_length <= 60:
            score += 25
        elif 10 <= title_length < 30 or 60 < title_length <= 70:
            score += 15
            issues.append({
                "id": "title-length",
                "icon": "fa-tag",
                "title": "Title Tag Length Suboptimal",
                "description": f"Title is {title_length} characters (optimal: 30-60).",
                "impact": "Medium - May affect click-through rate",
                "solution": "Adjust title length to 30-60 characters",
                "priority": "medium"
            })
        else:
            score += 5
            issues.append({
                "id": "title-length-poor",
                "icon": "fa-tag",
                "title": "Title Tag Length Poor",
                "description": f"Title is {title_length} characters.",
                "impact": "High - Affects search visibility",
                "solution": "Write a descriptive title (30-60 characters)",
                "priority": "high"
            })
    else:
        issues.append({
            "id": "missing-title",
            "icon": "fa-tag",
            "title": "Missing Title Tag",
            "description": "Pages without title tags are harder to rank.",
            "impact": "Critical - Affects search visibility",
            "solution": "Add a unique <title> to each page (50-60 chars)",
            "priority": "critical"
        })
    
    # Meta Description (25 points)
    description = meta_tags.get("description")
    desc_length = meta_tags.get("description_length", 0)
    
    if description:
        if 120 <= desc_length <= 160:
            score += 25
        elif 50 <= desc_length < 120 or 160 < desc_length <= 200:
            score += 15
            issues.append({
                "id": "description-length",
                "icon": "fa-file-lines",
                "title": "Meta Description Length Suboptimal",
                "description": f"Description is {desc_length} characters (optimal: 120-160).",
                "impact": "Medium - May affect CTR",
                "solution": "Adjust description length to 120-160 characters",
                "priority": "medium"
            })
        else:
            score += 5
    else:
        issues.append({
            "id": "missing-description",
            "icon": "fa-file-lines",
            "title": "Missing Meta Description",
            "description": "Meta descriptions influence click-through rates.",
            "impact": "High - Lower CTR from search results",
            "solution": "Add compelling meta description (120-160 chars)",
            "priority": "high"
        })
    
    # H1 Tag (25 points)
    h1_count = headings.get("h1_count", 0)
    
    if h1_count == 1:
        score += 25
    elif h1_count == 0:
        issues.append({
            "id": "missing-h1",
            "icon": "fa-heading",
            "title": "No H1 Heading Found",
            "description": "Every page should have exactly one H1.",
            "impact": "High - Confuses search engines about page topic",
            "solution": "Add exactly one <h1> with main keyword",
            "priority": "critical"
        })
    else:
        score += 10
        issues.append({
            "id": "multiple-h1",
            "icon": "fa-heading",
            "title": f"Multiple H1 Tags Detected ({h1_count})",
            "description": "Each page should have exactly one H1.",
            "impact": "Medium - Dilutes topic focus",
            "solution": "Keep only one H1 per page; use H2-H6 for subsections",
            "priority": "medium"
        })
    
    # H2+ Tags (25 points)
    h2_count = headings.get("h2_count", 0)
    h3_count = headings.get("h3_count", 0)
    
    if h2_count >= 2:
        score += 25
    elif h2_count >= 1:
        score += 20
    elif h3_count >= 1:
        score += 15
    else:
        score += 5
        issues.append({
            "id": "poor-heading-structure",
            "icon": "fa-list",
            "title": "Poor Heading Structure",
            "description": "Page lacks proper heading hierarchy (H2, H3).",
            "impact": "Medium - Poor content organization",
            "solution": "Use H2-H6 tags to structure your content logically",
            "priority": "medium"
        })
    
    # Word Count (bonus/penalty)
    word_count = raw.get("technical", {}).get("word_count", 0)
    if word_count < 300:
        score -= 10
        issues.append({
            "id": "thin-content",
            "icon": "fa-font",
            "title": "Thin Content",
            "description": f"Page has only {word_count} words (recommended: 1000+).",
            "impact": "Medium - Lower rankings for competitive keywords",
            "solution": "Expand content to at least 1000 words with valuable information",
            "priority": "medium"
        })
    
    return max(0, min(score, 100)), issues


def score_ux(raw: Dict[str, Any]) -> Tuple[int, List[Dict]]:
    """
    Calculer le score UX/UI (0-100)
    """
    score = 0
    issues = []
    
    images = raw.get("images", [])
    technical = raw.get("technical", {})
    
    # Find summary object in images array
    summary = next((i for i in images if i.get("_summary")), {})
    total_images = summary.get("total", 0)
    missing_alt = summary.get("missing_alt", 0)
    
    # Image Alt Text (30 points)
    if total_images > 0:
        alt_ratio = (total_images - missing_alt) / total_images
        
        if alt_ratio >= 0.9:
            score += 30
        elif alt_ratio >= 0.7:
            score += 22
            issues.append({
                "id": "some-images-missing-alt",
                "icon": "fa-image",
                "title": "Some Images Missing Alt Text",
                "description": f"{missing_alt} out of {total_images} images lack alt attributes.",
                "impact": "Medium - Poor accessibility",
                "solution": "Add descriptive alt text to all images",
                "priority": "medium"
            })
        elif alt_ratio >= 0.5:
            score += 15
            issues.append({
                "id": "many-images-missing-alt",
                "icon": "fa-image",
                "title": "Many Images Missing Alt Text",
                "description": f"{missing_alt} out of {total_images} images lack alt attributes.",
                "impact": "High - Poor accessibility + missed image SEO",
                "solution": "Add descriptive alt text to all images",
                "priority": "high"
            })
        else:
            score += 5
            issues.append({
                "id": "most-images-missing-alt",
                "icon": "fa-image",
                "title": "Most Images Missing Alt Text",
                "description": f"{missing_alt} out of {total_images} images lack alt attributes.",
                "impact": "Critical - Very poor accessibility",
                "solution": "Add descriptive alt text to all images immediately",
                "priority": "critical"
            })
    else:
        score += 25
    
    # Lazy Loading (20 points)
    lazy_loaded = summary.get("lazy_loaded", 0)
    if total_images > 5 and lazy_loaded > 0:
        score += 20
    elif total_images > 50 and lazy_loaded == 0:
        score += 0
        issues.append({
            "id": "many-images-no-lazy-loading",
            "icon": "fa-bolt",
            "title": "Many Images Without Lazy Loading",
            "description": f"{total_images} images were detected and none appear to use lazy loading.",
            "impact": "High - Heavy pages can feel slow on mobile and hurt engagement.",
            "solution": "Lazy-load below-fold images and prioritize only above-the-fold media.",
            "priority": "high"
        })
    elif total_images > 10 and lazy_loaded == 0:
        score += 5
        issues.append({
            "id": "no-lazy-loading",
            "icon": "fa-bolt",
            "title": "No Lazy Loading on Images",
            "description": "Large number of images without lazy loading.",
            "impact": "Medium - Slower page load",
            "solution": "Implement lazy loading for below-fold images",
            "priority": "medium"
        })
    else:
        score += 20
    
    # Language Attribute (20 points)
    if technical.get("has_lang"):
        score += 20
    else:
        score += 5
        issues.append({
            "id": "no-lang-attribute",
            "icon": "fa-language",
            "title": "Missing Language Attribute",
            "description": "The <html> tag should specify page language.",
            "impact": "Low - Minor accessibility impact",
            "solution": "Add lang attribute to <html> tag (e.g., <html lang=\"en\">)",
            "priority": "low"
        })
    
    # Favicon (20 points)
    if technical.get("has_favicon"):
        score += 15
    else:
        score += 5
        issues.append({
            "id": "no-favicon",
            "icon": "fa-image",
            "title": "Missing Favicon",
            "description": "Site has no favicon.",
            "impact": "Low - Minor branding impact",
            "solution": "Add a favicon to improve brand recognition",
            "priority": "low"
        })

    # Basic document encoding (10 points)
    if technical.get("has_charset"):
        score += 10
    else:
        issues.append({
            "id": "missing-charset",
            "icon": "fa-font",
            "title": "Missing Charset Declaration",
            "description": "The page does not expose a charset declaration in the crawled HTML.",
            "impact": "Low - Can cause text rendering issues for some browsers and languages.",
            "solution": "Add <meta charset=\"UTF-8\"> near the top of the <head>.",
            "priority": "low"
        })

    # Heavy HTML reduces perceived UX even when load time is currently fast.
    html_size_kb = technical.get("html_size_kb", 0)
    if html_size_kb > 300:
        score -= 10
        issues.append({
            "id": "large-html-document",
            "icon": "fa-file-code",
            "title": "Large HTML Document",
            "description": f"The HTML response is {html_size_kb:.0f} KB, which is heavy for an initial document.",
            "impact": "Medium - Large markup can slow parsing and interaction on weaker devices.",
            "solution": "Reduce initial markup, paginate large lists, and defer non-critical content.",
            "priority": "medium"
        })
    
    return max(0, min(score, 100)), issues


def score_popularity(raw: Dict[str, Any]) -> Tuple[int, List[Dict]]:
    """
    Calculer le score Popularity/Off-Page SEO (0-100)
    """
    score = 0
    issues = []
    
    links = raw.get("links", {})
    internal_links = links.get("internal", [])
    external_links = links.get("external", [])
    
    internal_count = len(internal_links)
    external_count = len(external_links)
    
    # Internal Linking (40 points)
    if internal_count >= 20:
        score += 40
    elif internal_count >= 10:
        score += 32
    elif internal_count >= 5:
        score += 24
    elif internal_count >= 2:
        score += 16
        issues.append({
            "id": "low-internal-linking",
            "icon": "fa-link",
            "title": "Low Internal Linking",
            "description": f"Only {internal_count} internal links found.",
            "impact": "Medium - Poor site navigation",
            "solution": "Add more internal links to related content",
            "priority": "medium"
        })
    else:
        score += 8
        issues.append({
            "id": "very-low-internal-linking",
            "icon": "fa-link",
            "title": "Very Low Internal Linking",
            "description": f"Only {internal_count} internal links found.",
            "impact": "High - Poor crawlability and user experience",
            "solution": "Significantly increase internal linking structure",
            "priority": "high"
        })
    
    # External Links (25 points)
    nofollow_count = sum(1 for link in external_links if link.get("is_nofollow"))
    
    if external_count >= 10:
        score += 25
    elif external_count >= 5:
        score += 20
    elif external_count >= 2:
        score += 15
    else:
        score += 8
        issues.append({
            "id": "low-external-links",
            "icon": "fa-arrow-up-right-from-square",
            "title": "Low External Links",
            "description": f"Only {external_count} external links found.",
            "impact": "Low - May indicate isolated content",
            "solution": "Link to authoritative sources when relevant",
            "priority": "low"
        })
    
    # Nofollow check (bonus)
    if external_count > 5 and nofollow_count == 0:
        issues.append({
            "id": "no-nofollow-links",
            "icon": "fa-link-slash",
            "title": "No Nofollow on External Links",
            "description": "Consider adding rel=\"nofollow\" to untrusted external links.",
            "impact": "Low - Minor SEO best practice",
            "solution": "Add rel=\"nofollow\" to external links you don't endorse",
            "priority": "low"
        })

    # The crawler only sees on-page link signals. Keep off-page popularity honest
    # unless future data providers add backlink/citation/domain authority metrics.
    score += 10
    issues.append({
        "id": "off-page-authority-not-measured",
        "icon": "fa-chart-line",
        "title": "Off-Page Authority Not Measured",
        "description": "Backlinks, citations, domain authority, and social mentions were not available from this crawl.",
        "impact": "Medium - Popularity score is based only on visible link signals, not full authority.",
        "solution": "Connect backlink or analytics data, then validate referring domains, anchor text, and institutional citations.",
        "priority": "medium"
    })
    
    return min(score, 100), issues


# =============================
# MAIN FUNCTION
# =============================
def compute_scores(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculer tous les scores SEO et générer les recommandations
    
    Args:
        raw_data (Dict): Données brutes du crawler
        
    Returns:
        Dict: Scores globaux, par catégorie, et issues
    """
    
    tech_score, tech_issues = score_technical(raw_data)
    content_score, content_issues = score_content(raw_data)
    ux_score, ux_issues = score_ux(raw_data)
    pop_score, pop_issues = score_popularity(raw_data)
    
    # Global score (weighted average)
    global_score = round(
        (tech_score * 0.35) +
        (content_score * 0.30) +
        (ux_score * 0.20) +
        (pop_score * 0.15)
    )
    
    typed_issues = (
        [{**issue, "category": "technical"} for issue in tech_issues] +
        [{**issue, "category": "content"} for issue in content_issues] +
        [{**issue, "category": "ux"} for issue in ux_issues] +
        [{**issue, "category": "popularity"} for issue in pop_issues]
    )

    # Categorize all issues by priority
    all_issues = {
        "critical": [i for i in typed_issues if i.get("priority") == "critical"],
        "high": [i for i in typed_issues if i.get("priority") == "high"],
        "medium": [i for i in typed_issues if i.get("priority") == "medium"],
        "low": [i for i in typed_issues if i.get("priority") == "low"]
    }
    
    return {
        "global_score": global_score,
        
        "categories": {
            "technical": tech_score,
            "content": content_score,
            "ux": ux_score,
            "popularity": pop_score
        },
        
        "issues": all_issues,
        
        "details": {
            "technical": {
                "score": tech_score,
                "issues_count": len(tech_issues)
            },
            "content": {
                "score": content_score,
                "issues_count": len(content_issues)
            },
            "ux": {
                "score": ux_score,
                "issues_count": len(ux_issues)
            },
            "popularity": {
                "score": pop_score,
                "issues_count": len(pop_issues)
            }
        }
    }


# =============================
# TEST
# =============================
if __name__ == "__main__":
    # Test data
    test_data = {
        "meta_tags": {
            "title": "Example Domain",
            "title_length": 14,
            "description": "This domain is for use in illustrative examples",
            "description_length": 48,
            "canonical": None,
        },
        "headings": {
            "h1": ["Example Domain"],
            "h1_count": 1,
            "h2": [],
            "h2_count": 0,
            "h3": [],
            "h3_count": 0,
        },
        "technical": {
            "load_time_ms": 500,
            "is_https": True,
            "has_viewport": False,
            "has_lang": False,
            "has_robots_txt": True,
            "has_sitemap": False,
            "has_structured_data": False,
            "has_favicon": True,
            "word_count": 28,
        },
        "images": [
            {"src": "/img1.jpg", "alt": "Image 1", "has_alt": True, "is_lazy": False},
            {"src": "/img2.jpg", "alt": None, "has_alt": False, "is_lazy": False},
            {"_summary": {"total": 2, "missing_alt": 1, "lazy_loaded": 0}}
        ],
        "links": {
            "internal": [{"url": "/page1"}, {"url": "/page2"}],
            "external": [{"url": "https://example.com", "is_nofollow": False}]
        },
        "performance": {
            "scripts_count": 5,
            "stylesheets_count": 3
        }
    }
    
    result = compute_scores(test_data)
    
    print("=" * 60)
    print("SEO SCORE RESULTS")
    print("=" * 60)
    print(f"\n📊 Global Score: {result['global_score']}/100")
    print(f"\n📈 Category Scores:")
    for cat, score in result['categories'].items():
        print(f"   {cat.capitalize()}: {score}/100")
    
    print(f"\n⚠️ Issues by Priority:")
    for priority, issues in result['issues'].items():
        if issues:
            print(f"   {priority.upper()}: {len(issues)} issues")
            for issue in issues[:3]:  # Show first 3
                print(f"      - {issue['title']}")
