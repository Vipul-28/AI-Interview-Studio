import re
import json
import base64
import urllib.request
from typing import Optional, Dict, Any, List


def extract_github_details(url: str) -> Optional[Dict[str, str]]:
    """Extracts owner and optional repo from a GitHub URL string."""
    if not url:
        return None
    url = url.strip()
    match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_\-\.]+)(?:/([a-zA-Z0-9_\-\.]+))?",
        url
    )
    if not match:
        return None

    owner = match.group(1).strip()
    repo = match.group(2).strip() if match.group(2) else None
    if repo and repo.endswith(".git"):
        repo = repo[:-4]

    return {"owner": owner, "repo": repo}


def fetch_repo_readme(owner: str, repo: str, headers: dict) -> str:
    """Helper to fetch and decode the README excerpt for a GitHub repository."""
    try:
        readme_api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        readme_req = urllib.request.Request(readme_api_url, headers=headers)
        with urllib.request.urlopen(readme_req, timeout=5) as rm_resp:
            rm_data = json.loads(rm_resp.read().decode("utf-8"))
            raw_content = rm_data.get("content", "")
            decoded = base64.b64decode(raw_content).decode("utf-8", errors="ignore")
            cleaned = re.sub(r"\[!\[.*?\]\(.*?\)\]\(.*?\)", "", decoded)
            return cleaned.strip()[:1400]
    except Exception as e:
        print(f"[GitHub Service] Could not fetch README for {owner}/{repo}: {e}")
        return ""


def extract_keywords(text: str) -> List[str]:
    """Extracts distinctive technical keywords from job description/title."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9\+\#\.\-]{2,}\b", text.lower())
    common_stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "are", "have",
        "will", "should", "our", "you", "your", "can", "role", "work", "team",
        "join", "years", "experience", "looking", "responsibilities", "skills",
        "required", "candidate", "must", "strong", "understanding"
    }
    return [w for w in set(words) if w not in common_stopwords]


def fetch_github_context(
    github_url: str,
    job_description: str = "",
    job_title: str = ""
) -> Optional[str]:
    """
    Fetches public metadata and README for a given GitHub repository or user profile.
    If a user profile is provided, it intelligently scans candidate repositories against
    job requirements to find and highlight the most relevant matching repository.
    """
    parsed = extract_github_details(github_url)
    if not parsed:
        return None

    owner = parsed["owner"]
    repo = parsed["repo"]
    headers = {
        "User-Agent": "AI-Interview-Studio/1.0",
        "Accept": "application/vnd.github.v3+json"
    }

    job_keywords = extract_keywords(f"{job_title} {job_description}")

    try:
        # Case 1: Specific Repository URL provided
        if repo:
            repo_api_url = f"https://api.github.com/repos/{owner}/{repo}"
            req = urllib.request.Request(repo_api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                repo_data = json.loads(response.read().decode("utf-8"))

            full_name = repo_data.get("full_name", f"{owner}/{repo}")
            description = repo_data.get("description") or "No description provided."
            primary_language = repo_data.get("language") or "General / Not specified"
            topics = ", ".join(repo_data.get("topics", [])) or "None specified"
            readme_excerpt = fetch_repo_readme(owner, repo, headers)

            # Check matching keywords
            combined_repo_text = f"{full_name} {description} {primary_language} {topics} {readme_excerpt}".lower()
            matched_terms = [kw for kw in job_keywords if kw in combined_repo_text]

            summary_lines = [
                f"=== SPECIFIC CANDIDATE REPOSITORY PROVIDED ===",
                f"Repository: {full_name}",
                f"Primary Stack: {primary_language}",
                f"Topics: {topics}",
                f"Description: {description}",
            ]
            if matched_terms:
                summary_lines.append(f"Technologies in Repo Matching Job Requirements: {', '.join(matched_terms[:10])}")
            if readme_excerpt:
                summary_lines.append(f"README Architecture & Feature Overview:\n{readme_excerpt}")
            summary_lines.append("==============================================")

            return "\n".join(summary_lines)

        # Case 2: Candidate User Profile URL provided (e.g. github.com/username)
        else:
            user_api_url = f"https://api.github.com/users/{owner}/repos?sort=updated&per_page=30"
            req = urllib.request.Request(user_api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                repos_data = json.loads(response.read().decode("utf-8"))

            if not repos_data:
                return f"Candidate GitHub Profile: github.com/{owner} (No public repositories found)"

            # Score each repo against job requirements
            scored_repos = []
            for r in repos_data:
                r_name = r.get("name") or ""
                r_lang = r.get("language") or ""
                r_desc = r.get("description") or ""
                r_topics = " ".join(r.get("topics", []))
                search_text = f"{r_name} {r_lang} {r_desc} {r_topics}".lower()

                # Calculate match score based on job requirements
                matches = [kw for kw in job_keywords if kw in search_text]
                score = len(matches)
                scored_repos.append({
                    "data": r,
                    "matches": matches,
                    "score": score
                })

            # Sort repos by highest match score first, then by stars/updates
            scored_repos.sort(
                key=lambda x: (x["score"], x["data"].get("stargazers_count", 0)),
                reverse=True
            )

            best_match = scored_repos[0]
            best_repo_data = best_match["data"]
            best_repo_name = best_repo_data.get("name")
            best_repo_full = best_repo_data.get("full_name")
            best_repo_lang = best_repo_data.get("language") or "General"
            best_repo_desc = best_repo_data.get("description") or "Candidate personal project"
            best_repo_topics = ", ".join(best_repo_data.get("topics", [])) or "None"

            # Fetch README for the best matching repo
            best_readme = fetch_repo_readme(owner, best_repo_name, headers)

            output_lines = [
                f"=== CANDIDATE GITHUB PROFILE: github.com/{owner} ===",
                f"AUTOMATICALLY MATCHED REPOSITORY TO JOB REQUIREMENTS:",
                f"- Repository Name: {best_repo_full}",
                f"- Tech Stack: {best_repo_lang} | Topics: {best_repo_topics}",
                f"- Description: {best_repo_desc}",
            ]

            if best_match["matches"]:
                output_lines.append(f"- Overlapping Skills Found: {', '.join(best_match['matches'][:10])}")
            if best_readme:
                output_lines.append(f"- README Highlights:\n{best_readme}")

            # Also list up to 3 other repositories
            other_repos = scored_repos[1:4]
            if other_repos:
                output_lines.append("\nOther Repositories on Candidate Profile:")
                for other in other_repos:
                    o_name = other["data"].get("name")
                    o_lang = other["data"].get("language") or "Code"
                    output_lines.append(f"- {o_name} ({o_lang})")

            output_lines.append("==================================================")
            return "\n".join(output_lines)

    except Exception as e:
        print(f"[GitHub Service] Failed to retrieve GitHub data for {github_url}: {e}")
        return f"Candidate GitHub URL: {github_url}"

    return None
