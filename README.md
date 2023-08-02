# SendGridReport

## Introduction

This script retrieves the last 24 hours of block and bounce events, and the
current month's SendGrid utilisation. It outputs on screen.

## Usage

This program uses the `sendgrid` and `python-dotenv` modules. Load into your
Windows environment with:

    py -m pip install python-dotenv sendgrid

Copy `.env.example` to `.env` and enter your SendGrid API key. Run with

    py SendGridReport.py
