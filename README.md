### Install dependencies

With Node.js and npm installed, run the following line from the root of the project:

```sh
npm install -g bower && npm install && bower install
```

### Development workflow
#### Run each command bellow in a console window.

```sh
npm run-script jsx
npm run-script bundle
npm run-script serve
cd backend/iluminare && python manage.py makemigrations && python manage.py migrate && python manage.py runserver
```

## Contributing

We welcome your bug reports, PRs for improvements, docs and anything you think would improve the experience of the project.
