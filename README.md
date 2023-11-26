# BizCardX-Extracting-Business-Card-Data-with-OCR

## Overview

This project aims to develop a Streamlit application that streamlines the extraction of relevant information from business cards uploaded by users. Leveraging the power of easyOCR, the application will intelligently extract details such as company name, cardholder name, designation, contact information, address, and more. The extracted data will be neatly displayed in a graphical user interface (GUI) for user convenience.


## Features
User-Friendly Interface: The application boasts a simple and intuitive UI that guides users seamlessly through the process of uploading a business card image and extracting information.

Data Extraction: Utilizing the easyOCR library, the application extracts key details including company name, cardholder name, designation, mobile number, email address, website URL, area, city, state, and pin code.

Database Integration: Users can save the extracted information into a database along with the uploaded business card image. The database, powered by SQLite or MySQL, is designed to store multiple entries, each associated with its respective business card image and extracted information.

CRUD Operations: The application supports essential CRUD (Create, Read, Update, Delete) operations. Users can easily add, view, update, and delete entries through the Streamlit UI.

## Technologies Used
- Python: The core programming language for application logic.
- Streamlit: A powerful framework for building interactive web applications with minimal effort.
- easyOCR: The OCR library used for extracting information from business card images.
- Database Management System: Choose between SQLite or MySQL for efficient storage and retrieval of extracted data.
