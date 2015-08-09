
var React = require('react');
var Router = require('react-router'),
  Route = Router.Route,
  RouteHandler = Router.RouteHandler,
  Link = Router.Link;

let pacienteIntent = require('./intent/Paciente');
let pacienteModel = require('./stores/PacienteStore')(pacienteIntent);
let PacienteCheckin = require('./components/paciente/PacienteCheckin.react')(pacienteModel);
let PacienteDetails = require('./components/paciente/PacienteDetails.react')(pacienteModel);

let instanciaTratamentoIntent = require('./intent/InstanciaTratamento');
let instanciaTratamentoModel = require('./stores/InstanciaTratamentoStore')(instanciaTratamentoIntent);

let atendimentoIntent = require('./intent/Atendimento');
let atendimentoModel = require('./stores/AtendimentoStore')(atendimentoIntent);
let Atendimento = require('./components/atendimento/Atendimento.react')(instanciaTratamentoModel);
let AtendimentosList = require('./components/atendimento/AtendimentosList.react')(atendimentoModel);
let AtendimentoConfirm = require('./components/atendimento/AtendimentoConfirm.react')(atendimentoModel);

var routes = (
  <Route>
    <Route path="paciente" handler={PacienteCheckin} />
    <Route path="paciente/details/:id" handler={PacienteDetails} />
    <Route path="atendimento" handler={Atendimento} />
    <Route path="atendimento/confirm/:id" handler={AtendimentoConfirm} />
    <Route path="atendimentos/:id" handler={AtendimentosList} />
    <Route path="voluntario" handler={Atendimento} />
    <Route path="relatorio" handler={Atendimento} />
  </Route>
);

Router.run(routes, function (Handler) {
  React.render(<Handler/>, document.getElementById('react-content'));
});
