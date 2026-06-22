# docker-bake.hcl
# Medium-term approach to keep root Dockerfile, .devcontainer, and CI in sync.
# Usage:
#   docker buildx bake prod          # production image (default target)
#   docker buildx bake dev           # dev image (like .devcontainer)
#   docker buildx bake ci            # CI/test image
#   docker buildx bake --print       # see resolved config
#   NODE_VERSION=20.19 PYTHON_VERSION=3.10 docker buildx bake

variable "NODE_VERSION" {
  default = "20"
}

variable "PYTHON_VERSION" {
  default = "3.9"
}

group "default" {
  targets = ["prod"]
}

group "all" {
  targets = ["prod", "dev", "ci"]
}

target "common" {
  args = {
    NODE_VERSION   = NODE_VERSION
    PYTHON_VERSION = PYTHON_VERSION
  }
}

# Production image (root Dockerfile)
target "prod" {
  inherits = ["common"]
  dockerfile = "Dockerfile"
  target     = "final"
  tags       = ["meal-planner:prod"]
}

# Development / devcontainer image
target "dev" {
  inherits = ["common"]
  dockerfile = ".devcontainer/Dockerfile"
  target     = "final"
  tags       = ["meal-planner:dev"]
}

# CI / test image (uses devcontainer base for full dev deps + test tools)
target "ci" {
  inherits = ["common"]
  dockerfile = ".devcontainer/Dockerfile"
  target     = "final"
  tags       = ["meal-planner:ci"]
}
