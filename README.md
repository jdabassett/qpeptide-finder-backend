<div align="center">
  <img src="assets/images/qpeptide_finger_logo_transparent_medium.png" alt="QPeptide Finder Logo" width="200"/>

  # QPeptide Finder API

  **A FastAPI-based backend service for quantitative proteomics peptide selection and analysis**

  [![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.120+-00a398.svg)](https://fastapi.tiangolo.com/)
  [![Poetry](https://img.shields.io/badge/poetry-2.2.1-60a5fa.svg)](https://python-poetry.org/)
  [![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)](https://www.docker.com/)
  [![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)](https://www.mysql.com/)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

## Description

The **QPeptide Finder API** is a specialized backend service designed to analyze protein sequences and evaluate the suitability of each resulting peptide for use as a quantitative proteomics peptide (QPeptide). As the core processing engine of the QPeptide Finder service, this API performs computationally intensive peptide analysis, maintains comprehensive records of all digests and evaluations, and serves as the data layer for the frontend application.

#### What It Does

When provided with a protein sequence and protease type, the service:

1. **Digests the protein** - Generates all possible peptides based on the specified protease cleavage rules
2. **Evaluates each peptide** - Applies 14 distinct scientific criteria filters to assess peptide quality (see [Science](#science) section for details)
3. **Calculates peptide attributes** - Computes physical and chemical properties including isoelectric point (pI), charge state, and hydrophobicity scores
4. **Ranks peptides** - Assigns a weighted ranking to each peptide based on how many criteria it meets, helping researchers identify the most suitable candidates
5. **Stores results** - Persists all digest jobs, peptides, and evaluation criteria in a MySQL database for retrieval and analysis

#### Architecture

The service is built with **FastAPI** for high-performance async request handling, uses **SQLAlchemy** for database operations, and leverages **MySQL** for reliable data persistence. It's containerized with **Docker** for easy deployment and can be scaled horizontally to handle increased load.

## Science

#### Quantitative Proteomics with Heavy Isotope-Labeled Peptides

Quantitative proteomics aims to measure the absolute abundance of proteins across different samples. One of the most accurate methods for achieving this is using **heavy isotope-labeled peptides** (QPeptides) as internal standards in Liquid Chromatography-tandem Mass Spectrometry (LC-MS/MS) analysis.

![Quantitative Proteomics Workflow](assets/images/quantitative_protemics_diagrma.png)

#### The Workflow

The process begins with **sample preparation**: multiple biological samples (e.g., control vs. treated conditions) are processed to extract proteins. These proteins are then digested with trypsin (or another protease) to break them down into smaller peptide fragments.

**Here's where QPeptides come in**: Before the samples can be analyzed, suitable peptides must be:

1. **Identified** - Selected from the protein sequence based on scientific criteria
2. **Ordered** - Synthesized with heavy isotope labels (typically using stable isotopes like 13C, 15N, or 2H)
3. **Spiked in** - Added to the peptide mixture at known concentrations

Once the heavy isotope-labeled QPeptides are added to the sample mixture, the entire preparation undergoes LC-MS/MS analysis. The mass spectrometer can distinguish between the **light peptides** (from the biological samples) and the **heavy peptides** (the QPeptides) because they have different mass-to-charge ratios, despite being chemically identical.

#### Why This Matters

During LC-MS/MS analysis, both the light and heavy versions of each peptide are detected. Since the heavy QPeptide is added at a known concentration, the ratio of light-to-heavy peptide signal intensity directly reflects the absolute abundance of the protein in the original sample. This allows researchers to *DIRECTLY* quantify protein levels across different experimental conditions.

**The critical step**: Identifying the right peptides to use as QPeptides is essential, as not all peptides are suitable for quantitative analysis. This is where the QPeptide Finder API comes in - it automates the complex process of evaluating thousands of potential peptides against scientific criteria to identify the best candidates for synthesis and use as internal standards.

#### Peptide Selection Criteria

The service evaluates each peptide against 14 scientifically-validated criteria to ensure optimal performance in LC-MS/MS quantification:

- **Sequence uniqueness** - Ensures the peptide uniquely identifies the target protein
- **Chemical stability** - Avoids peptides prone to modifications (e.g., methionine oxidation, cysteine alkylation)
- **Fragmentation characteristics** - Selects peptides that produce informative MS/MS spectra
- **MS detectability** - Optimizes for peptides with favorable charge states, pI values, and hydrophobicity

Peptides are ranked based on how many criteria they meet, with higher-ranked peptides being the most suitable candidates for synthesis as QPeptides.


## Getting Started

#### Prerequisites

Before you begin, ensure you have the following installed on your machine:

- **Docker** (version 20.10 or later) and **Docker Compose** (version 2.0 or later)
- **Git** for cloning the repository
- (Optional) **Poetry** (version 2.2.1 or later) if you want to run the application locally without Docker

#### Installation

1. **Clone the repository**
   ```
   git clone git@github.com:jdabassett/qpeptide-finder-backend.git
   cd qpeptide-cutter-backend
   ```
2. **Set up environment variables**

   Copy the example environment file and customize it as needed:
   ```
   cp .env.example .env
   ```
      Then edit the `.env` file with your configuration. The `docker-compose.local.yml` file includes default development settings, so you can also run the application without creating a `.env` file if you're using the default configuration.

3. **Start the services**

   Using Docker Compose, this will start both the MySQL database and the FastAPI backend:
   ```
   docker-compose -f docker-compose.local.yml up --build
   ```
      This command will:
   - Build the backend Docker image
   - Start a MySQL 8.0 container
   - Automatically create the database and run migrations
   - Start the FastAPI server on port 8000

4. **Verify the installation**

   Once the containers are running, you should see output indicating that migrations have completed and the server has started. You can verify the API is working by visiting:

   - **API Documentation (Swagger UI)**: http://localhost:8000/docs
   - **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health

#### Running in the Background

To run the services in detached mode (in the background):
```
# build container
docker-compose -f docker-compose.local.yml up -d --build
# view logs
docker-compose -f docker-compose.local.yml logs -f
# destroy container
docker-compose -f docker-compose.local.yml down
```

#### First Steps

Once the API is running, you can:

1. **Explore the API documentation** at http://localhost:8000/docs to see all available endpoints
2. **Create a user** using the `/api/v1/users` endpoint
3. **Submit a digest job** with a protein sequence using the `/api/v1/digest/job` endpoint
4. **Retrieve results** once the job completes using the `/api/v1/digest/peptides/{digest_id}` endpoint

#### Testing

The project includes comprehensive test coverage with both unit and integration tests. Tests use an in-memory SQLite database for fast execution and data isolation.

#### Running Tests

**Using Poetry** (recommended for local development):

#### Run all tests
```
poetry run pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author & Attribution

**Jacob Bassett**

A full-stack software engineer with a background in molecular biology, specializing in backend development with Python. This project combines expertise in both software engineering and quantitative proteomics to create tools that benefit scientific research.

#### Connect

[![Portfolio](https://img.shields.io/badge/Portfolio-000000?style=for-the-badge&logo=About.me&logoColor=white)](https://jacobbassett-portfolio.netlify.app/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jacobbassett/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jdabassett)

#### Acknowledgments


This project was developed to address real challenges in quantitative proteomics research. Special thanks to the following individuals their contributions as my molecular biology mentors.

- [Jeff Ranish, PhD](https://www.linkedin.com/in/jeff-ranish-55b9781b)
- [Jie Luo, PhD](https://www.linkedin.com/in/jie-luo-7aa8524a)
- [Mark Gillespie, PhD](https://www.linkedin.com/in/gillespiem)

"If I have seen further, it is by standing on the shoulders of giants." - Sir Isaac Newton



## FRONTEND COMING SOON
