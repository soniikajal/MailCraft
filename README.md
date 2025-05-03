# MailCraft

A lightweight email marketing tool for small businesses, built with Python and Gmail API integration.


# Description
MailCraftt is a simple yet powerful email marketing solution designed specifically for small businesses who want professional newsletters without the complexity or cost of enterprise platforms. It started as a custom solution for a handmade business but has evolved into a versatile tool that any small business can use.


# Features
HTML email template support
Subscriber management via CSV
Multiple email types (welcome, newsletter, promotion, update)
Personalized content delivery
Batch sending to avoid rate limits
Test emails before campaign launch
Campaign summary reporting


# Requirements
Python 3.6+
Google account with Gmail
Google Cloud Platform project with Gmail API enabled


# Installation

Clone this repository
git clone https://github.com/soniikajal/mailcraft.git
cd mailcraft

# Install required packages

pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
Set up Google Cloud Platform project and enable Gmail API
Create a project in Google Cloud Console
Enable the Gmail API
Create OAuth credentials (Desktop app)
Download the credentials.json file and place it in the project directory


# Usage
Prepare your subscribers.csv file with at least name and email columns
Create or modify the newsletter.html template

# Run the script:
python mailcraft.py
Follow the prompts to select email type, customize subject, and send your campaign


# Configuration
Edit the top section of mailcraft.py to configure your business information:
text

SENDER_EMAIL = "your.email@gmail.com"
BUSINESS_NAME = "Your Business Name"
BUSINESS_PHONE = "Your Phone Number"
BUSINESS_EMAIL = "your.email@gmail.com"
BUSINESS_WEBSITE = "https://yourbusiness.com"
BUSINESS_SOCIAL = "https://www.instagram.com/yourbusiness"


# Project Status
This project is in active development. Future enhancements may include:
Unsubscribe link handling
More template options
