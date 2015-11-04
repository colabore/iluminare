var React = require('react');
var ReactDOM = require('react-dom');
var ReactRouter = require('react-router'),
  Route = ReactRouter.Route,
  Router = ReactRouter.Router,
  Link = ReactRouter.Link;

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

ReactDOM.render(<Router>
  <Route path="paciente" component={PacienteCheckin} />
  <Route path="paciente/details/:id" component={PacienteDetails} />
  <Route path="tratamento" handler={Tratamento} />
  <Route path="tratamento/details/:id" component={TratamentoDetails} />
  <Route path="atendimento" component={Atendimento} />
  <Route path="atendimento/confirm/:id" component={AtendimentoConfirm} />
  <Route path="atendimentos/:id" component={AtendimentosList} />
  <Route path="voluntario" component={Atendimento} />
  <Route path="relatorio" component={Atendimento} />
</Router>, document.getElementById('react-content'));
