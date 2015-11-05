const Rx = require('rx');
const Observable = Rx.Observable;
const React = require('react');
const MaterialUI = require('material-ui');
const List = MaterialUI.List;
const ListItem = MaterialUI.ListItem;
const Tabs = MaterialUI.Tabs;
const Tab = MaterialUI.Tab;
const injectTapEventPlugin = require("react-tap-event-plugin");
injectTapEventPlugin();

const requests = require('../../requests');
const routes = require('../../utils/routes')

const request$ = new Rx.Subject();
const interval$ = Observable.interval(10000).startWith(0);
const requestInterval$ = Observable.combineLatest(interval$, request$).map(x => x[1]);
const response$ = requestInterval$.
  flatMap(x => requests.requestAtendimentoFromTratamentoId(x));

const description = [
  {
    status: 'C',
    label: 'Check-in',
    empty: 'Nenhum paciente que fez check-in está esperando para ser chamado.',
    nonempty: 'pacientes fizeram check-in e não foram chamados.'
  },{
    status: 'X',
    label: 'Chamado',
    empty: 'Nenhum paciente foi chamado e não entrou ainda.',
    nonempty: 'pacientes foram chamados.'
  },{
    status: 'A',
    label: 'Atendido',
    empty: 'Nínguem foi atendido ainda.',
    nonempty: 'pacientes foram atendidos.'
  },{
    status: 'N',
    label: 'Não Atendido',
    empty: 'Nínguem desistiu.',
    nonempty: 'pacientes desistiram.'
  },{
    status: 'I',
    label: 'Impresso',
    empty: 'Nenhum papel foi gasto com esse tratamento hoje.',
    nonempty: 'pacientes estão na lista.'
  }
]

var sub1;
var sub2;

const Atendimentos = React.createClass({
  getInitialState: function() {
    return { atendimento: [] };
  },
  componentDidMount: function() {
    sub1 = response$.subscribe(this.setState.bind(this));
    sub2 = request$.onNext(this.props.params.id);
  },
  componentWillUnmount: function() {
    if (sub1)
      sub1.dispose();
    if (sub2)
      sub2.dispose();
  },
  _onTouchTap: function(e){
    routes.goTo('/atendimento/confirm/' + e.currentTarget.id);
  },
  _toListitems: function(row) {
    return (
      <ListItem
        key={row.id}
        id={row.id}
        onTouchTap={this._onTouchTap}
        secondaryText={
          'Chegou às ' + row.hora_chegada +
          ', para o tratamento ' + row.instancia_tratamento.tratamento.descricao_basica}>
        Senha {row.senha}{row.status}: {row.paciente.nome}
      </ListItem>
    )
  },
  _items: function(description) {
    const items = this.state.atendimento.filter(x => x.status === description.status);
    const listItems = items.map(this._toListitems);
    return (
      <Tab label={description.label} >
        { items.length > 0 && <p>{items.length} {description.nonempty}</p> }
        { items.length == 0 && <p>{description.empty}</p> }
        <List> {listItems} </List>
      </Tab>
    )
  },
  render: function() {
    return (
      <Tabs>
        { this._items(description[0]) }
        { this._items(description[1]) }
        { this._items(description[2]) }
        { this._items(description[3]) }
        { this._items(description[4]) }
      </Tabs>
    )
  }
});

module.exports = Atendimentos;
