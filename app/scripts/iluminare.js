var React = require('react');
var ReactDOM = require('react-dom');
var ReactRouter = require('react-router'),
  Route = ReactRouter.Route,
  Router = ReactRouter.Router;

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
let AtendimentoConfirm = require('./view/atendimento/AtendimentoConfirm.react')(
                                 atendimentoModel, tratamentoModel);

const atendimento$ = require('./components/Atendimento/Atendimento');
const Atendimentos = require('./components/Atendimentos/Atendimentos');

const Html = React.createClass({
  getInitialState: function() {
   return { html: <h1>loading...</h1> };
  },
  componentDidMount: function() {
    this.props.html.subscribe(x => this.setState({ html: x }));
  },
  render: function() {
    return this.state.html;
  }
});

const Atendimento = (props) => { return ( <Html html={atendimento$} /> ); }

ReactDOM.render(<Router>
  <Route path="paciente" component={PacienteCheckin} />
  <Route path="paciente/details/:id" component={PacienteDetails} />
  <Route path="tratamento" handler={Tratamento} />
  <Route path="tratamento/details/:id" component={TratamentoDetails} />
  <Route path="atendimento" component={Atendimento} />
  <Route path="atendimento/confirm/:id" component={AtendimentoConfirm} />
  <Route path="atendimentos/:id" component={Atendimentos} />
  <Route path="voluntario" component={Atendimento} />
  <Route path="relatorio" component={Atendimento} />
</Router>, document.getElementById('react-content'));
