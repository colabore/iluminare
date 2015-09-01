var React = require('react');
var Router = require('react-router'),
  Route = Router.Route,
  RouteHandler = Router.RouteHandler,
  Link = Router.Link;

let pacienteIntent = require('./intent/Paciente');
let pacienteModel = require('./model/Paciente')(pacienteIntent);
let PacienteCheckin = require('./view/paciente/PacienteCheckin.react')(pacienteModel);
let PacienteDetails = require('./view/paciente/PacienteDetails.react')(pacienteModel);

let instanciaTratamentoIntent = require('./intent/InstanciaTratamento');
let instanciaTratamentoModel = require('./model/InstanciaTratamento')(instanciaTratamentoIntent);

let tratamentoModel = require('./model/Tratamento')();
let Tratamento = require('./view/tratamento/Tratamento.react')(tratamentoModel);
let TratamentoDetails = require('./view/tratamento/TratamentoDetails.react')(
  {tratamento: tratamentoModel, instanciatratamento: instanciaTratamentoModel});

let atendimentoIntent = require('./intent/Atendimento');
let atendimentoModel = require('./model/Atendimento')(atendimentoIntent);
let Atendimento = require('./view/atendimento/Atendimento.react')(instanciaTratamentoModel);
let AtendimentosList = require('./view/atendimento/AtendimentosList.react')(atendimentoModel);
let AtendimentoConfirm = require('./view/atendimento/AtendimentoConfirm.react')(
                                 atendimentoModel, tratamentoModel);

var routes = (
  <Route>
    <Route path="paciente" handler={PacienteCheckin} />
    <Route path="paciente/details/:id" handler={PacienteDetails} />
    <Route path="tratamento" handler={Tratamento} />
    <Route path="tratamento/details/:id" handler={TratamentoDetails} />
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
