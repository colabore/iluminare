
var React = require('react');
var PacienteActions = require('../../actions/PacienteActions');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  TextField = MaterialUI.TextField;

var ENTER_KEY_CODE = 13;

var PacienteSearch = React.createClass({
  childContextTypes: {muiTheme: React.PropTypes.object},
  getChildContext: function() {return {muiTheme: ThemeManager.getCurrentTheme()}},

  handleChange: function($event) {
    if ($event.keyCode == ENTER_KEY_CODE)
      $event.preventDefault();

    PacienteActions.search($event.target.value);
  },

  render: function() {
    return (
      <TextField
        fullWidth={true}
        hintText="digite o nome do paciente para fazer o check-in"
        floatingLabelText="Nome do paciente"
        onChange={this.handleChange} />
    )
  }
})

module.exports = PacienteSearch;
