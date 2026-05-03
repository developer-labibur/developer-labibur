"""Technology catalog for the interactive setup wizard."""

from __future__ import annotations

TECH_CATALOG = {
    "Frontend": [
        "React", "Vue.js", "Angular", "Svelte", "Next.js", "Nuxt.js",
        "Astro", "HTML", "CSS", "SCSS", "Tailwind CSS", "Bootstrap",
    ],
    "Backend": [
        "Node.js", "Python", "Go", "Rust", "Java", "C#", "Ruby", "PHP",
        "Elixir", "Kotlin",
    ],
    "Mobile": [
        "React Native", "Flutter", "Swift", "Kotlin", "Dart",
    ],
    "Database": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "DynamoDB",
        "Cassandra",
    ],
    "DevOps & Cloud": [
        "Docker", "Kubernetes", "Terraform", "AWS", "GCP", "Azure",
        "GitHub Actions", "GitLab CI", "Jenkins",
    ],
    "Data & ML": [
        "Pandas", "NumPy", "TensorFlow", "PyTorch", "Scikit-learn", "Spark",
    ],
    "Languages": [
        "TypeScript", "JavaScript", "Python", "Go", "Rust", "Java", "C++",
        "C", "Ruby", "PHP", "Scala", "Haskell", "Lua", "Zig",
    ],
    "Tools": [
        "Git", "Vim", "VS Code", "Linux", "Nginx", "GraphQL", "REST", "gRPC",
    ],
}


def get_all_techs() -> list[str]:
    """Return a unique sorted list of all technologies across categories."""
    return sorted({tech for techs in TECH_CATALOG.values() for tech in techs})
