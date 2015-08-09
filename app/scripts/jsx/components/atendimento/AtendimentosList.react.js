var React = require('react');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  ListItem = MaterialUI.ListItem,
  List = MaterialUI.List,
  DropDownMenu = MaterialUI.DropDownMenu;
var injectTapEventPlugin = require("react-tap-event-plugin");
injectTapEventPlugin();

var model;
var subscription;

var AtendimentosList = React.createClass({
  childContextTypes: {
    muiTheme: React.PropTypes.object
  },
  getChildContext: function() {
    return { muiTheme: ThemeManager.getCurrentTheme() }
  },
  getInitialState: function() {
    return {results: []};
  },
  componentDidMount: function() {
    model.byInstanciaTratamentoIdAction.onNext(this.props.params.id);
    subscription = model.byInstanciaTratamentoIdStore.subscribe(this.setState.bind(this));
  },
  componentWillUnmount: function() {
    subscription.dispose();
  },
  _onTouchTap: function(e) {
    document.location = document.location.origin + '/#/atendimento/confirm/' + e.currentTarget.id;
  },
  _transform: function(row) {
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
  render: function () {
    var items = this.state.results.map(this._transform);

    var description = (items.length > 0)
      ? <p>{this.state.count} atendimento(s) não confirmado(s) do tratamento
        <strong> {this.state.results[0].instancia_tratamento.tratamento.descricao_basica} </strong>
        para a data {this.state.results[0].instancia_tratamento.data}</p>
      : <p>Ninguém fez o checkin para o tratamento ainda</p>;

    return (
      <div>
        {description}
        <List>
          {items}
        </List>
      </div>
    )
  }
});

function create(options) {
  if (!options.byInstanciaTratamentoIdAction)
    throw new Error('byInstanciaTratamentoIdAction is required');

  if (!options.byInstanciaTratamentoIdStore)
    throw new Error('byInstanciaTratamentoIdStore is required');

  model = options;
  return AtendimentosList;
}

module.exports = create;
