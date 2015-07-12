var React = require('react');
var InstanciaTratamentoStore = require('../../stores/InstanciaTratamentoStore');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  List = MaterialUI.List,
  ListItem = MaterialUI.ListItem;

var InstanciaTratamentoPanel = React.createClass({
  childContextTypes: {muiTheme: React.PropTypes.object},
  getChildContext: function() {return {muiTheme: ThemeManager.getCurrentTheme()}},
  getInitialState: function() {
   return InstanciaTratamentoStore.get();
  },
  componentDidMount: function() {
    InstanciaTratamentoStore.addChangeListener(this._onData);
  },
  componentWillUnmount: function() {
    InstanciaTratamentoStore.removeChangeListener(this._onData);
  },
  _onTouchTap: function(e) {
    //PacienteActions.info(e.currentTarget.id);
    document.location = document.location.origin + '/#/atendimentos/' + e.currentTarget.id;
  },
  _onData: function() {
    this.setState(InstanciaTratamentoStore.get());
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
    return (
      <List>
        {items}
      </List>
    )
  }
});

module.exports = InstanciaTratamentoPanel;
