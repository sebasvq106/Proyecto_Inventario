# Web Platform for Managing Loaned Items at the EIE Warehouse

This project is a web platform designed to manage the loan of items from the warehouse of the School of Electrical Engineering (EIE) at the University of Costa Rica. Its objective is to digitize and optimize a loan process that was previously handled through physical documents.

---

## Table of Contents

1. [Proposed Solution](#proposed-solution)
2. [Installation & Setup](#installation--setup)
3. [Usage](#usage)
4. [Running Jobs](#running-jobs)
5. [Diagrams](#diagrams)
6. [Technologies Used](#technologies-used)
7. [Contact Information](#contact-information)
8. [Notes](#notes)

---

## Proposed Solution

The platform enables different roles (students, professors, warehouse staff, and administrators) to interact efficiently with the warehouse system.

### Features by Role

* **Students**: View available items, create loan orders, collaborate in group orders.
* **Professors**: Create and manage student groups, view class-related orders.
* **Administrators**: Add/remove items, manage user orders, verify pending orders, manage users and assign roles.

### Diagrams

* **Use Case Diagram**
  ![Use case diagram](Docs/use_case_diagram.png)

* **State Diagram**
  ![State diagram for a requested item](Docs/item_after_request_diagram.png)

* **Database Schema**
  ![Database](Docs/database.png)

---

## Installation & Setup

### Clone Repository

```bash
git clone https://github.com/christabel-alvarado/Proyecto_Inventario.git
cd Proyecto_Inventario
```

### Docker Setup

Ensure you have Docker and Docker Compose installed.

#### 1. Build and Start the Containers

```bash
docker-compose up --build
```

#### 2. Stop the Containers

To stop the running containers:

```bash
docker-compose down
```

#### 3. Apply Migrations & Create Superuser

Once the containers are up:

```bash
docker-compose exec web python manage.py migrate
```

#### 4. Load Seed Data

The file `seeds.json` has the initial data to use the page. Use the following command:

```bash
docker-compose exec web python manage.py seed
```

---

## Usage

* Visit: `http://localhost:8000`
* Log in with your admin or user credentials.
* Use the admin panel: `http://localhost:8000/admin` to manage models manually.
* Professors can manage groups, students can create shared orders, and warehouse staff can manage inventory.

---

## Running Jobs

The platform include scheduled jobs.

To run jobs:

```bash
docker-compose exec web python manage.py crontab add
```

And to see the jobs that are running at the moment:

```bash
docker-compose exec web python manage.py crontab show
```

---

## Technologies Used

* Python 3.10.12
* Django 5.0.4
* PostgreSQL
* Docker & Docker Compose
* HTML, TailwindCSS, JavaScript

---

## Contact Information

### Technical Supervisor

* **M.Sc. Marco Villalta Fallas**
* Email: [soporte.eie@ucr.ac.cr](mailto:soporte.eie@ucr.ac.cr)

### Project Supervisor

* **Ph.D. Fausto Calderón Obaldía**
* Email: [fausto.calderonobaldia@ucr.ac.cr](mailto:fausto.calderonobaldia@ucr.ac.cr)

### Main Contributor

* **Christabel Alvarado Anchía**
* Email: [christabel.alvarado@ucr.ac.cr](mailto:christabel.alvarado@ucr.ac.cr)

### Developer

* **Sebastián Vargas Quesada**
* Email: [sebastian.vargasquesada@ucr.ac.cr](mailto:sebastian.vargasquesada@ucr.ac.cr)

---

## Notes

Future improvements may include user analytics, API endpoints, and integration with the university's authentication system. The repository may eventually migrate to the official Git server of the University of Costa Rica.
