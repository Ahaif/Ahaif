#!/usr/bin/env python3
"""Refresh public profile statistics using GitHub REST API (stdlib only)."""
import collections
import json
import os
from pathlib import Path
import urllib.request
from xml.sax.saxutils import escape

OWNER = "Ahaif"
ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
  "Systems, Algorithms & Low-Latency": [
    "order_book",
    "ft_IRC",
    "minishell",
    "Dining_Philosophers",
    "STL_containers",
    "Push_swap",
    "Pipex",
    "mini_talk",
    "libft",
    "ft_printf",
    "get_next_line",
    "cpp_modules"
  ],
  "Web & Applications": [
    "ft_transcendence",
    "Task_tracker",
    "interns_crud_TT",
    "csv_minerTT",
    "front_test_TT"
  ],
  "Blockchain & Smart Contracts": [
    "Exchange_Market",
    "wledbablah"
  ],
  "Infrastructure & Backend": [
    "Inception-Docker",
    "air_space_guardian"
  ],
  "Graphics & Rendering": [
    "Cub3d",
    "FDF"
  ],
  "AI & Data": [
    "Python-ML",
    "fcode_bot"
  ],
  "Cybersecurity": [
    "CS-Pool"
  ]
}
FEATURED = [["order_book","Concurrent Rust matching engine with WebSocket API and benchmarks"],["ft_IRC","Event-driven C++98 IRC server with non-blocking sockets"],["air_space_guardian","Fault-tolerant Rust drone-monitoring backend"],["CS-Pool","Web security, reverse engineering and security exercises"],["Exchange_Market","Ethereum smart-contract exchange"],["Cub3d","C raycasting and 3D rendering"]]
def api(path):
    headers = {"Accept":"application/vnd.github+json","User-Agent":"Ahaif-profile-stats"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request("https://api.github.com"+path,headers=headers),timeout=30) as response:
        return json.load(response)

def repositories():
    found = {}
    for page in range(1,11):
        batch = api(f"/users/{OWNER}/repos?per_page=100&page={page}&type=owner")
        for repo in batch:
            if repo["owner"]["login"].lower() == OWNER.lower() and not repo["private"] and not repo["fork"] and repo["name"] != OWNER:
                found[repo["name"]] = repo
        if len(batch)<100:
            break
    return found

def main():
    repos = repositories()
    assigned = [name for names in GROUPS.values() for name in names]
    if len(set(assigned)) != len(assigned):
        raise RuntimeError("Duplicate repository in categories")
    missing = set(assigned)-set(repos)
    if missing:
        raise RuntimeError("Missing or no longer original/public: "+", ".join(sorted(missing)))
    other = sorted(set(repos)-set(assigned))
    totals = collections.Counter()
    for name in sorted(repos):
        data = api(f"/repos/{OWNER}/{name}/languages")
        totals.update({k:v for k,v in data.items() if isinstance(v,int) and v>0})
    grand = sum(totals.values())
    if grand == 0:
        raise RuntimeError("No language data: refusing to publish empty statistics")
    ordered = sorted(totals.items(),key=lambda p:(-p[1],p[0]))
    width=760
    height=100+len(ordered)*30
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Programming language distribution">',
         '<rect width="100%" height="100%" rx="14" fill="#0d1117"/>',
         '<text x="24" y="34" fill="#e6edf3" font-size="21" font-family="Arial,sans-serif" font-weight="bold">Programming languages</text>',
         '<text x="24" y="55" fill="#8b949e" font-size="12" font-family="Arial,sans-serif">Public non-fork projects · GitHub language bytes</text>']
    colors=["#58a6ff","#3fb950","#d2a8ff","#ffa657","#f778ba","#79c0ff"]
    for i,(language,bytes_count) in enumerate(ordered):
        y=78+i*30
        pct=100*bytes_count/grand
        svg.extend([f'<text x="24" y="{y+12}" fill="#e6edf3" font-size="13" font-family="Arial,sans-serif">{escape(language)}</text>',
          f'<rect x="255" y="{y}" width="385" height="14" rx="7" fill="#21262d"/>',
          f'<rect x="255" y="{y}" width="{max(1,round(385*pct/100))}" height="14" rx="7" fill="{colors[i%len(colors)]}"/>',
          f'<text x="730" y="{y+12}" text-anchor="end" fill="#e6edf3" font-size="13" font-family="Arial,sans-serif">{pct:.1f}%</text>'])
    svg.append("</svg>")
    (ROOT/"assets").mkdir(exist_ok=True)
    (ROOT/"assets/languages.svg").write_text("\n".join(svg)+"\n",encoding="utf-8")
    n=len(repos)
    lines=["# Ahaif","","### Software Systems Engineer · Low-Latency Systems · Cybersecurity · Blockchain","","Building reliable, secure and performance-oriented software across systems programming, networking, distributed systems and backend infrastructure.","","## Programming languages","","![Programming language distribution](assets/languages.svg)","","Language percentages are calculated from GitHub-reported code bytes across public non-fork projects, not development time or proficiency.","","## Project portfolio","",f"**{n} original public projects** · Grouped by purpose and technical similarity.","","| Engineering domain | Projects | Share |","|---|---:|---:|"]
    for domain,names in GROUPS.items():
        lines.append(f"| {domain} | {len(names)} | {100*len(names)/n:.1f}% |")
    if other:
        lines.append(f"| New / uncategorized | {len(other)} | {100*len(other)/n:.1f}% |")
    lines.extend(["","> Portfolio percentages count repositories, not language bytes.","","## Featured engineering projects",""])
    for name,description in FEATURED:
        lines.append(f"- **[{name}](https://github.com/{OWNER}/{name})** — {description}")
    lines.extend(["","## Explore projects by engineering domain",""])
    for domain,names in GROUPS.items():
        lines.extend([f"### {domain}",""," · ".join(f"[{name}](https://github.com/{OWNER}/{name})" for name in names),""])
    if other:
        lines.extend(["### New / uncategorized",""," · ".join(f"[{name}](https://github.com/{OWNER}/{name})" for name in other),""])
    lines.extend(["## Engineering principles","","Secure-by-design architecture · SOLID principles · Concurrency and performance · Fault tolerance · Automated testing","",f"[Browse public repositories](https://github.com/{OWNER}?tab=repositories)",""])
    (ROOT/"README.md").write_text("\n".join(lines),encoding="utf-8")
    print(f"Updated {n} projects and {len(ordered)} language percentages")

if __name__=="__main__":
    main()
