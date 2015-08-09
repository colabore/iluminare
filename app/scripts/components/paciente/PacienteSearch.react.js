
var React = require('react');
var TextField = require('material-ui').TextField;

var ENTER_KEY_CODE = 13;

var PacienteSearch = React.createClass({
  handleChange: function($event) {
    if ($event.keyCode == ENTER_KEY_CODE)
      $event.preventDefault();

    this.props.searchByNameAction.onNext($event.target.value);
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
