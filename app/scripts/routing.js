window.addEventListener('WebComponentsReady', function() {

  // We use Page.js for routing. This is a Micro
  // client-side router inspired by the Express router
  // More info: https://visionmedia.github.io/page.js/
  page('/', function () {
    app.route = 'home';
  });

  page('/paciente', function () {
    app.route = 'paciente';
    app.params = {'path': 'Pacientes'}
  });

  page('/paciente/:id/details', function (data) {
    app.route = 'paciente-details';
    app.params = {'path': 'Pacientes / detalhe paciente'};
  });

  page('/paciente/details', function (data) {
    app.route = 'paciente-details';
    app.params = {'path': 'Pacientes / detalhe paciente'};
  });

  page('/atendimento', function () {
    app.route = 'atendimento';
    app.params = {'path': 'Atendimentos'};
  });

  page('/voluntario', function () {
    app.route = 'voluntario';
    app.params = {'path': 'Voluntários'};
  });

  page('/relatorio', function () {
    app.route = 'relatorio';
    app.params = {'path': 'Relatórios'};
  });

  // add #! before urls
  page({
    hashbang: true
  });

});
