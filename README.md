# Ridesharing by Dhiraj Amin

# Ride Sharing and CO2 Emissions

This project, developed for the IBM SkillsBuild Virtual Faculty Buildathon 2023 in the Cloud App Development track with Red Hat OpenShift, is a Flask-based ridesharing application. The application is containerized using Docker and orchestrated with Red Hat OpenShift Kubernetes.

## Features

- **Landing Page:** The landing page provides an overview of the application's functionality, features, and emphasizes the role of ridesharing in reducing CO2 emissions.

- **User Authentication:** Users can register and log in to the website to access personalized features.

- **Statistics Dashboard:** Upon login, users gain access to a comprehensive statistics dashboard displaying relevant information about rideshare activities.

- **CO2 Emission Calculator:** Users can calculate CO2 emissions based on the selected vehicle type, promoting environmental awareness.

- **Ride Management:** Users can publish ride offers, expressing their willingness to share rides with others. Additionally, a search functionality allows users to find shared rides based on location and dates and book available rides.

## Technology Stack

- **Framework:** Flask
- **Containerization:** Docker
- **Orchestration:** Red Hat OpenShift Kubernetes

In this project ibm db2 is used for database operations and images are stored and retrieved from ibm cloud storage. The code docker image is created and pushed to 
dockerhub : https://hub.docker.com/layers/dhirajaminm/ibmnov23fdpr/0.0.2.Release/images/sha256-1063c9e82689f3b9e35cca651c8290b020db5a19c47098612eed079478f145ed?context=explore

The same Docker container is employed within Red Hat OpenShift for the deployment of the web application.


Available online at : https://ibmnov23fdpr-dhiraja-dev.apps.sandbox-m3.1530.p1.openshiftapps.com/

User can login using username: passpwrd :- dibm/dibm



Badges as per requirement
DevOps for Enterprise Business Agility: https://www.credly.com/badges/48bda7ad-602d-4174-a00d-62d10dca850d/public_url
Journey to Cloud: Envisioning Your Solution: https://www.credly.com/badges/c14e99e6-bd77-44d9-b0c8-d49cccd9cae9/public_url
