# lcog-hr

# Set up a Postgres server locally
1) Download Postgres and pgAdmin apps
2) Follow these steps: https://djangocentral.com/using-postgresql-with-django/
    -Create a database called 'hr_app'
    -Create a DB user for the DB
    -Set defaults for user (e.g. utf-8) and grant DB permissions to user
3) Set DB name, username, and password in settings_local


# Run the backend locally
Activate the virtual environment
`source env/bin/activate` 
Start the server
`./manage.py runserver`

# Run the frontend locally
`cd frontend`
`quasar dev`

# Deploy backend
In mainsite/middleware/CorsMiddleware, make sure the correct response["Access-Control-Allow-Origin"] is commented out.
`eb deploy --profile lcog`

# Deploy frontend
`cd frontend`
`quasar build`
Navigate to https://s3.console.aws.amazon.com/s3/buckets/lcog-hr-frontend/
Under the 'Objects' tab is the list of files
Drag the contents of frontend/dist/spa to the window to upload the build

# Testing
Run frontend end-to-end tests
`npm run cypress:open`

# Production Sites
Production Frontend - http://lcog-hr-frontend.s3-website-us-west-2.amazonaws.com
Production API - http://lcog-internal-env.eba-4t9yrmiu.us-west-2.elasticbeanstalk.com/api/
Production Backend - http://lcog-internal-env.eba-4t9yrmiu.us-west-2.elasticbeanstalk.com/admin/