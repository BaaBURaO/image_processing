# Image Processing System

## Overview

This project is an image processing system that uses FastAPI for the web framework, SQLAlchemy for ORM, and Google Cloud Storage for image storage. The system processes CSV files containing image URLs, compresses the images, and uploads them to Google Cloud Storage.

## Components

1. **FastAPI Application**: Provides endpoints for file uploads and status checks.
2. **PostgreSQL Database**: Stores metadata about file and image processing requests.
3. **Google Cloud Storage**: Used for storing compressed images.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/image-processing-system.git
   cd image-processing-system
