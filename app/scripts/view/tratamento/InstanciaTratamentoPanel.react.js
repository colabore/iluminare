var React = require('react');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  List = MaterialUI.List,
  ListItem = MaterialUI.ListItem;

var subscription;

var InstanciaTratamentoPanel = React.createClass({
  childContextTypes: {
    muiTheme: React.PropTypes.object
  },
  getChildContext: function() {
    return {
      muiTheme: ThemeManager.getCurrentTheme()
    }
  },
  getInitialState: function() {
   return {results: []};
  },
  componentDidMount: function() {
    subscription = this.props.todayStore.subscribe(this.setState.bind(this));
  },
  componentWillUnmount: function() {
    subscription.dispose();
  },
  _onTouchTap: function(e) {
    //PacienteActions.info(e.currentTarget.id);
    document.location = document.location.origin + '/#/atendimentos/' + e.currentTarget.id;
  },
  _getListItem: function(data) {
    return (
      <ListItem
        id={data.id}
        key={data.id}
        secondaryText={data.data}
        onTouchTap={this._onTouchTap}>
        {data.tratamento.descricao_basica}
      </ListItem>
    );
  },
  render: function() {
    var items = this.state.results.map(this._getListItem);
    var descricao = items.length > 0 ? "" : <p>Nenhum tratamento foi aberto hoje.</p>;
    return (
      <div>
        <h4>Tratamentos em progresso</h4>
        {descricao}
        <List>
          {items}
        </List>
      </div>
    )
  }
});

module.exports = InstanciaTratamentoPanel;
