export const ROLE_PRESETS = [
  {
    id: "software_engineer",
    title: "Full Stack Software Engineer",
    icon: "💻",
    category: "Engineering",
    isSoftwareEngineer: true,
    description:
      "Design, develop, and maintain robust scalable web applications. Build responsive user interfaces with modern frontend frameworks and high-performance REST APIs. Write clean testable code, optimize database queries, and collaborate using Git and CI/CD pipelines.",
    githubPlaceholder: "https://github.com/username/project-repo",
  },
  {
    id: "data_scientist",
    title: "Data Scientist & AI / ML Engineer",
    icon: "📊",
    category: "AI & Analytics",
    isSoftwareEngineer: true,
    description:
      "Develop and deploy machine learning models, statistical analyses, and predictive pipelines using Python, PyTorch/TensorFlow, and SQL. Conduct feature engineering, fine-tune models, evaluate metrics, and translate complex data findings into actionable insights.",
    githubPlaceholder: "https://github.com/username/ml-project",
  },
  {
    id: "product_manager",
    title: "Technical Product Manager",
    icon: "🚀",
    category: "Product",
    isSoftwareEngineer: false,
    description:
      "Define product strategy, build feature roadmaps, and prioritize backlog using data-driven metrics. Author comprehensive PRDs, gather customer feedback, and coordinate cross-functional teams across engineering, UX design, and business leadership.",
    githubPlaceholder: "",
  },
  {
    id: "ui_ux_designer",
    title: "UI/UX & Product Designer",
    icon: "🎨",
    category: "Design",
    isSoftwareEngineer: false,
    description:
      "Design intuitive, user-centered digital experiences. Create wireframes, interactive user flows, and high-fidelity design systems in Figma. Lead usability studies, synthesize user research, and maintain consistent visual accessibility standards.",
    githubPlaceholder: "",
  },
  {
    id: "devops_engineer",
    title: "DevOps & Cloud Solutions Engineer",
    icon: "☁️",
    category: "Infrastructure",
    isSoftwareEngineer: true,
    description:
      "Architect and scale cloud infrastructure on AWS/GCP using Terraform. Automate resilient CI/CD deployment pipelines, manage container orchestration with Docker and Kubernetes, and implement proactive observability with Prometheus and Grafana.",
    githubPlaceholder: "https://github.com/username/infrastructure-repo",
  },
  {
    id: "hr_talent",
    title: "HR & Talent Acquisition Lead",
    icon: "👥",
    category: "Operations",
    isSoftwareEngineer: false,
    description:
      "Drive full-cycle technical recruiting, employer branding, and candidate onboarding. Partner with hiring managers on headcount planning, conduct structured behavioral screenings, and champion diversity, equity, and company culture initiatives.",
    githubPlaceholder: "",
  },
  {
    id: "custom",
    title: "Custom Role",
    icon: "⚙️",
    category: "Custom",
    isSoftwareEngineer: false,
    description: "",
    githubPlaceholder: "https://github.com/username/repository (Optional)",
  },
];
