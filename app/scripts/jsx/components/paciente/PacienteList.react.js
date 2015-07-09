
var React = require('react');
var PacienteSearchStore = require('../../stores/PacienteSearchStore');
var PacienteActions = require('../../actions/PacienteActions');
injectTapEventPlugin = require("react-tap-event-plugin");
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
  },
  getMessageListItem: function(message) {
    return (
      <ListItem
        id={message.pk}
        key={message.pk}
        secondaryText={message.fields.data_nascimento}
        onTouchTap={this._onTouchTap}>
        {message.fields.nome}
      </ListItem>
    );
  },
  render: function() {
    var messageListItems = this.state.result.map(this.getMessageListItem);
    return (
      <List>
        {messageListItems}
      </List>
    )
  }
});

module.exports = PacienteList;
