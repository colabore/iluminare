### Install dependencies

With Node.js and npm installed, run the following line from the root of the project:

```sh
npm install -g bower && npm install && bower install
```

### Development workflow
#### Run each command bellow in a console window.

```sh
npm run serve1
cd backend/iluminare && python manage.py makemigrations && python manage.py migrate && cd ../../
npm run serve2
npm run serve3
```

```npm run serve1```: web server for the ```app/``` static resources at localhost:3000.

```npm run serve2```: api server at localhost:8000.

```npm run serve3```: legacy version of iluminare at localhost:8080.

## Contributing

We welcome your bug reports, PRs for improvements, docs and anything you think would improve the experience of the project.
