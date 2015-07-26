
var React = require('react');
var Rx = require('rx');
var Router = require('react-router'),
  Route = Router.Route,
  RouteHandler = Router.RouteHandler,
  Link = Router.Link;

var PacientesSearchByNameAction = new Rx.Subject();
var PacientesSearchByNameStore = new Rx.Subject();
var PacienteInfoAction = new Rx.Subject();
var PacienteInfoStore = new Rx.Subject();

var InstanciaTratamentosByDateAction = new Rx.Subject();
var InstanciaTratamentosByDateStore = new Rx.Subject();

var AtendimentosByIdAction = new Rx.Subject();
var AtendimentosByIdStore = new Rx.Subject();

var PacienteStore = require('./stores/PacienteStore')({
  searchByNameAction: PacientesSearchByNameAction,
  searchByNameStore: PacientesSearchByNameStore,
  infoAction: PacienteInfoAction,
  infoStore: PacienteInfoStore
});

var InstanciaTratamentoStore = require('./stores/InstanciaTratamentoStore')({
  byDateAction: InstanciaTratamentosByDateAction,
  byDateStore: InstanciaTratamentosByDateStore
});

var AtendimentoStore = require('./stores/AtendimentoStore')({
  byIdAction: AtendimentosByIdAction,
  byIdStore: AtendimentosByIdStore
});

var PacienteCheckin = require('./components/paciente/PacienteCheckin.react');
var PacienteCheckinHander = React.createClass({
  render() {
    return <PacienteCheckin
      searchByNameAction={PacientesSearchByNameAction}
      searchByNameStore={PacientesSearchByNameStore}
      infoAction={PacienteInfoAction} />
  }
});

var PacienteDetails = require('./components/paciente/PacienteDetails.react');
var PacienteDetailsHandler = React.createClass({
  componentDidMount: function() {
    PacienteInfoAction.onNext(this.props.params.id);
  },
  render() {
    return <PacienteDetails infoStore={PacienteInfoStore} />
  }
});

var Atendimento = require('./components/atendimento/Atendimento.react');
var AtendimentoHander = React.createClass({
  componentDidMount: function() {
    InstanciaTratamentosByDateAction.onNext(new Date());
  },
  render() {
    return <Atendimento todayStore={InstanciaTratamentosByDateStore} />
  }
});

var AtendimentosList = require('./components/atendimento/AtendimentosList.react');
var AtendimentosListHandler = React.createClass({
  componentDidMount: function() {
    AtendimentosByIdAction.onNext(this.props.params.id);
  },
  render() {
    return <AtendimentosList atendimentosStore={AtendimentosByIdStore} />
  }
});

var routes = (
  <Route>
    <Route path="paciente" handler={PacienteCheckinHander} />
    <Route path="paciente/details/:id" handler={PacienteDetailsHandler} />
    <Route path="atendimento" handler={AtendimentoHander} />
    <Route path="atendimentos/:id" handler={AtendimentosListHandler} />
    <Route path="voluntario" handler={AtendimentoHander} />
    <Route path="relatorio" handler={AtendimentoHander} />
  </Route>
);

Router.run(routes, function (Handler) {
  React.render(<Handler/>, document.getElementById('react-content'));
});
