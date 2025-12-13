#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(__file__))
EXAMPLE_DIR = os.path.join(ROOT, 'example')


def latex_to_text(s: str) -> str:
    """Convert LaTeX to plain text."""
    if not s:
        return s
    # \textcolor{...}{inner} -> inner
    s = re.sub(r"\\textcolor\{[^}]*\}\{([\s\S]*?)\}", r"\1", s)
    # \textbf{...}, \textit{...}, etc -> inner
    s = re.sub(r"\\text\w+\{([\s\S]*?)\}", r"\1", s)
    # \website{url}{text} -> text
    s = re.sub(r"\\website\{[^}]*\}\{([^}]*)\}", r"\1", s)
    # \github{user} -> user
    s = re.sub(r"\\github\{([^}]*)\}", r"\1", s)
    # \textbar -> |
    s = s.replace("\\textbar{}", "|")
    s = s.replace("\\textbar", "|")
    # TeX escapes
    s = s.replace("\\&", "&")
    # Remove braces carefully (handle nested)
    depth = 0
    result = []
    for ch in s:
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth = max(0, depth - 1)
        else:
            result.append(ch)
    s = ''.join(result)
    # Remove remaining backslashes and unknown commands
    s = re.sub(r"\\[a-zA-Z]+", "", s)
    # Normalize spaces
    s = re.sub(r"\s+", " ", s).strip()
    return s


def smart_split_commas(s: str) -> list:
    """Split by commas but keep text inside parentheses together."""
    parts = []
    buf = []
    depth = 0
    for ch in s:
        if ch in '({':
            depth += 1
            buf.append(ch)
        elif ch in ')}':
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch == ',' and depth == 0:
            part = ''.join(buf).strip()
            if part:
                parts.append(part)
            buf = []
        else:
            buf.append(ch)
    if buf:
        part = ''.join(buf).strip()
        if part:
            parts.append(part)
    return parts


def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ''


def extract_balanced_braces(text: str, start_pos: int) -> str:
    """Extract content within balanced braces starting from start_pos (after opening brace)."""
    depth = 0
    end_pos = start_pos
    for i in range(start_pos, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            if depth == 0:
                end_pos = i
                break
            depth -= 1
    return text[start_pos:end_pos]


def extract_name_and_tagline(cv_tex: str):
    name_match = re.search(r"\\name\{([^}]*)\}\{([^}]*)\}", cv_tex)
    tagline_match = re.search(r"\\tagline\{", cv_tex)
    name = None
    if name_match:
        name = f"{name_match.group(1).strip()} {name_match.group(2).strip()}"
    tagline = None
    if tagline_match:
        start = tagline_match.end()
        tagline_raw = extract_balanced_braces(cv_tex, start)
        tagline = latex_to_text(tagline_raw)
    return name, tagline


def extract_socialinfo(cv_tex: str):
    block_match = re.search(r"\\socialinfo\{([\s\S]*?)\}", cv_tex)
    socials = {}
    if not block_match:
        return socials
    block = block_match.group(1)
    # Simple extractors
    for key in ['linkedin', 'github', 'smartphone', 'email', 'address', 'infos']:
        m = re.search(r"\\%s\{([^}]*)\}" % key, block)
        if m:
            socials[key] = latex_to_text(m.group(1).strip())
    return socials


def load_experience():
    # prefer long form if present, else short
    path_long = os.path.join(EXAMPLE_DIR, 'section_experience.tex')
    path_short = os.path.join(EXAMPLE_DIR, 'section_experience_short.tex')
    content = read_file(path_long) or read_file(path_short)
    if not content:
        return []
    entries = []
    # Pattern: \experience{start}{role}{company}{location}{end}{...description...}{tags}
    # The description block can contain itemize/begin/end, so use non-greedy matching
    exp_re = re.compile(
        r"\\experience\s*\n\s*\{([^}]*)\}\s*\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\s*\n\s*\{([^}]*)\}\s*\{([\s\S]*?)\}\s*\{([^}]*)\}",
        re.MULTILINE
    )
    for m in exp_re.finditer(content):
        start, role, company, location, end, desc, tags = m.groups()
        dates = f"{start.strip()} - {end.strip()}" if start.strip() and end.strip() else (start.strip() or end.strip())
        
        # Extract bullet points from itemize environment
        bullets = []
        for line in desc.split('\n'):
            line = line.strip()
            if line.startswith('\\item'):
                bullet_text = line.replace('\\item', '').strip()
                cleaned = latex_to_text(bullet_text)
                if cleaned:
                    bullets.append(cleaned)
        
        entries.append({
            'role': latex_to_text(role.strip()),
            'company': latex_to_text(company.strip()),
            'location': latex_to_text(location.strip()),
            'dates': latex_to_text(dates),
            'bullets': bullets,
            'tags': [latex_to_text(t.strip()) for t in smart_split_commas(tags)]
        })
    return entries


def load_education():
    path = os.path.join(EXAMPLE_DIR, 'section_scolarite.tex')
    content = read_file(path)
    entries = []
    # Find all \scholarshipentry commands
    for m in re.finditer(r"\\scholarshipentry\s*\{", content):
        start = m.end()
        # Extract first field (dates)
        dates = extract_balanced_braces(content, start)
        # Find second field (details) 
        next_brace = content.find('{', start + len(dates) + 1)
        if next_brace == -1:
            continue
        details = extract_balanced_braces(content, next_brace + 1)
        entries.append({'dates': latex_to_text(dates.strip()), 'details': latex_to_text(details.strip())})
    return entries


def load_skills():
    path = os.path.join(EXAMPLE_DIR, 'section_competences.tex')
    content = read_file(path)
    # Parse \keywordsentry{Category}{Items}
    items = []
    for m in re.finditer(r"\\keywordsentry\{([^}]*)\}\{([^}]*)\}", content):
        cat, vals = m.groups()
        cat = latex_to_text(cat.strip())
        vals = latex_to_text(vals.strip())
        items.append({'category': cat, 'items': [latex_to_text(v.strip()) for v in smart_split_commas(vals)]})
    return items


def load_awards():
    path = os.path.join(EXAMPLE_DIR, 'section_awards.tex')
    content = read_file(path)
    awards = []
    # Find all \scholarshipentry commands
    for m in re.finditer(r"\\scholarshipentry\s*\{", content):
        start = m.end()
        # Extract first field (year)
        year = extract_balanced_braces(content, start)
        # Find second field (title) 
        next_brace = content.find('{', start + len(year) + 1)
        if next_brace == -1:
            continue
        title = extract_balanced_braces(content, next_brace + 1)
        awards.append({'year': year.strip(), 'title': latex_to_text(title.strip())})
    return awards


def load_headline():
    # Prefer English headline archi
    path_archi = os.path.join(EXAMPLE_DIR, 'section_headline_archi.tex')
    txt = read_file(path_archi).strip()
    if txt:
        # strip LaTeX \par{ ... }
        m = re.search(r"\\par\{([\s\S]*?)\}", txt)
        return latex_to_text(m.group(1).strip() if m else txt)
    # Fallback French headline
    path = os.path.join(EXAMPLE_DIR, 'section_headline.tex')
    txt = read_file(path).strip()
    m = re.search(r"\\par\{([\s\S]*?)\}", txt)
    return latex_to_text(m.group(1).strip() if m else txt)


def load_languages_and_strengths():
    path = os.path.join(EXAMPLE_DIR, 'section_langues.tex')
    content = read_file(path)
    langs = []
    for m in re.finditer(r"\\skill\{([^}]*)\}\{([^}]*)\}", content):
        name, level = m.groups()
        langs.append({'language': name.strip(), 'level': level.strip()})
    strengths = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('\\item'):
            s = latex_to_text(line.replace('\\item', '').strip())
            if s:
                strengths.append(s)
    return langs, strengths


def extract_links(links_raw: str) -> dict:
    r"""Extract URLs and text from \website{} and \github{} commands."""
    links = {}
    
    # Extract \website{url}{display_text}
    for m in re.finditer(r"\\website\{([^}]*)\}\{([^}]*)\}", links_raw):
        url, display = m.groups()
        links['website'] = {'url': url.strip(), 'display': display.strip()}
    
    # Extract \github{username} or \github{org/repo}
    for m in re.finditer(r"\\github\{([^}]*)\}", links_raw):
        github_path = m.group(1).strip()
        links['github'] = {
            'url': f"https://github.com/{github_path}",
            'display': github_path
        }
    
    return links


def load_projects():
    path = os.path.join(EXAMPLE_DIR, 'section_projets.tex')
    content = read_file(path)
    projects = []
    # Pattern: \project{title}{dates}{links}{description}{tech}
    # Multi-line with proper brace matching
    proj_re = re.compile(
        r"\\project\s*\n\s*\{([^}]*)\}\{([^}]*)\}\s*\n\s*\{([\s\S]*?)\}\s*\n\s*\{([\s\S]*?)\}\s*\n\s*\{([^}]*)\}",
        re.MULTILINE
    )
    for m in proj_re.finditer(content):
        title, dates, links, desc, techs = m.groups()
        links_dict = extract_links(links)
        projects.append({
            'title': latex_to_text(title.strip()),
            'dates': latex_to_text(dates.strip()),
            'links': links_dict,
            'description': latex_to_text(re.sub(r"\s+", " ", desc.strip())),
            'tech': [latex_to_text(t.strip()) for t in smart_split_commas(techs) if t.strip()],
        })
    return projects


def load_publications():
    # Minimal pass-through of bib entries for consumer rendering
    bib = read_file(os.path.join(EXAMPLE_DIR, 'my_publications.bib'))
    entries = []
    # Capture type, key, author, title, year, book/journal
    pat = re.compile(r"@(INPROCEEDINGS|ARTICLE)\{([^,]+),[\s\S]*?author\s*=\s*\{([\s\S]*?)\},[\s\S]*?title\s*=\s*\{([\s\S]*?)\},([\s\S]*?)year\s*=\s*\{([^}]*)\}", re.MULTILINE)
    for m in pat.finditer(bib):
        typ, key, author, title, middle, year = m.groups()
        journal = None
        booktitle = None
        jm = re.search(r"journal\s*=\s*\{([^}]*)\}", middle)
        bm = re.search(r"booktitle\s*=\s*\{([^}]*)\}", middle)
        if jm:
            journal = jm.group(1).strip()
        if bm:
            booktitle = bm.group(1).strip()
        entries.append({
            'type': typ.lower(),
            'key': key,
            'author': latex_to_text(author.strip()),
            'title': latex_to_text(title.strip()),
            'year': latex_to_text(year.strip()),
            'journal': latex_to_text(journal) if journal else None,
            'booktitle': latex_to_text(booktitle) if booktitle else None,
        })
    return entries


def main():
    cv_tex = read_file(os.path.join(EXAMPLE_DIR, 'cv.tex'))
    name, tagline = extract_name_and_tagline(cv_tex)
    socials = extract_socialinfo(cv_tex)
    data = {
        'name': name,
        'tagline': tagline,
        'socials': socials,
        'headline': load_headline(),
        'experience': load_experience(),
        'education': load_education(),
        'skills': load_skills(),
        'awards': load_awards(),
        'languages': load_languages_and_strengths()[0],
        'strengths': load_languages_and_strengths()[1],
        'projects': load_projects(),
        'publications': load_publications(),
        'meta': {
            'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        }
    }
    out_dir = os.path.join(ROOT, 'public')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'cv.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path}")


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
