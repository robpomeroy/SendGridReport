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

## AWS Lambda

The `lambda_function.py` file is a version of the script that can run on AWS
Lambda, as-is. Set the `SENDGRID_API_KEY` environment variable in the Lambda
function definition. Use `Lambda-Build-Layer.bat` to create a zip file
containing the libraries required by the script when running within Lamba.
Upload this file to a layer and ensure the Lambda function is configured to use
it.
