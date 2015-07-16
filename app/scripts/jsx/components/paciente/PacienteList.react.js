
var React = require('react');
var PacienteSearchStore = require('../../stores/PacienteSearchStore');
var PacienteActions = require('../../actions/PacienteActions');
var injectTapEventPlugin = require("react-tap-event-plugin");
injectTapEventPlugin();

var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  List = MaterialUI.List,
  ListItem = MaterialUI.ListItem;

var PacienteList = React.createClass({
  childContextTypes: {muiTheme: React.PropTypes.object},
  getChildContext: function() {return {muiTheme: ThemeManager.getCurrentTheme()}},

  getInitialState: function() {
   return PacienteSearchStore.get();
  },
  componentDidMount: function() {
    PacienteSearchStore.addChangeListener(this._onData);
  },
  componentWillUnmount: function() {
    PacienteSearchStore.removeChangeListener(this._onData);
  },
  _onData: function() {
    this.setState(PacienteSearchStore.get());
  },
  _onTouchTap: function(e) {
    PacienteActions.info(e.currentTarget.id);
    document.location = document.location.origin + '/#/paciente/details/' + e.currentTarget.id;
  },
  getMessageListItem: function(data) {
    return (
      <ListItem
        id={data.id}
        key={data.id}
        secondaryText={data.data_nascimento}
        onTouchTap={this._onTouchTap}>
        {data.nome}
      </ListItem>
    );
  },
  render: function() {
    var messageListItems = this.state.results.map(this.getMessageListItem);
    return (
      <List>
        {messageListItems}
      </List>
    )
  }
});

module.exports = PacienteList;
