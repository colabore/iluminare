var React = require('react');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  ListItem = MaterialUI.ListItem,
  List = MaterialUI.List;

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
    subscription = this.props.atendimentosStore.subscribe(this.setState.bind(this));
  },
  componentWillUnmount: function() {
    subscription.dispose();
  },
  _transform: function(row) {
    return (
      <ListItem
        key={row.senha}
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
      ? <p>Atendimentos não confirmados do tratamento
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

module.exports = AtendimentosList;
