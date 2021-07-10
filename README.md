# lcog-hr

# Run the backend locally
`source ../env/bin/activate && ./manage.py runserver`

# Run the frontend locally
`cd frontend && quasar dev`

# Cypress e2e tests
Open Cypress launcher to run individual tests
`cd frontend && npm run cypress:open`
Run Cypress tests in the background and upload results to https://dashboard.cypress.io/
`cd frontend && npm run cypress:run`

# Deploy backend
In mainsite/middleware/CorsMiddleware, make sure the correct response["Access-Control-Allow-Origin"] is commented out.
`source ../env/bin/activate`
`eb deploy --profile lcog`

# Deploy frontend
`cd frontend`
`quasar build`
Navigate to https://s3.console.aws.amazon.com/s3/buckets/team.lcog.org/
Under the 'Objects' tab is the list of files
Drag the contents of frontend/dist/spa to the window to upload the build

# Production Sites
Production Frontend - http://team.lcog.org.s3-website-us-west-2.amazonaws.com
Production API - http://lcog-internal-env.eba-4t9yrmiu.us-west-2.elasticbeanstalk.com/api/
Production Backend - http://lcog-internal-env.eba-4t9yrmiu.us-west-2.elasticbeanstalk.com/admin/