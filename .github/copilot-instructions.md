# GitHub Copilot Custom Instructions

## Project Overview

- This repository contains two main services:
  - `services/mankkoo-ui`: A Next.js frontend application (React-based).
  - `services/mankkoo`: A Flask backend (Python) with PostgreSQL database.

## General Guidelines

- Prioritize clean, readable, and maintainable code.
- Use clear naming conventions and concise comments where necessary.
- Follow the separation of concerns principle.
- Write modular, reusable components and functions.
- Ensure robust error handling and input validation.

## Next.js (Frontend) Best Practices

- Use functional components and React hooks.
- Prefer TypeScript for type safety.
- Organize components in a feature-based folder structure.
- Leverage Next.js features: 
  - Use `app/` directory (if using Next.js 13+) for routing and layouts.
  - Prefer server components for data fetching when possible.
  - Use `getServerSideProps`, `getStaticProps`, or API routes for data fetching as appropriate.
- Optimize performance with code-splitting, lazy loading, and image optimization (`next/image`).
- Ensure accessibility (ARIA attributes, semantic HTML).
- Use environment variables for configuration (never hardcode secrets).
- Handle API requests using fetch or Axios, with clear separation of API logic.

## Flask (Backend) Best Practices

- Use the application factory pattern for scalable app structure.
- Organize code with blueprints for modularity.
- Use psycog2 for database interaction.
- Apply input validation with Marshmallow.
- Use environment variables for configuration (never commit secrets).
- Implement robust error handling and logging.
- Write unit and integration tests with pytest.
- Follow RESTful API design principles.
- Use connection pooling for PostgreSQL.
- Document API endpoints (e.g., with Swagger/OpenAPI).

## PostgreSQL Guidelines

- Use appropriate data types and indexes for performance.
- Write migrations using Alembic.
- Avoid raw SQL queries unless necessary; always use parameterized queries.
- Regularly analyze and vacuum the database.
- Keep database credentials and configuration in environment variables.
- Follow naming conventions for tables and columns.

## Integration

- Use CORS middleware in Flask to allow requests from the frontend.
- Clearly separate frontend and backend logic.
- Use DevContainer for local development if possible.
- Document setup and deployment steps in the repository.

## Code Quality

- Use linters and formatters: 
  - Next.js: ESLint, Prettier.
  - Flask: flake8, black.
- Ensure all code is covered by automated tests before merging.
- Write clear, concise commit messages.