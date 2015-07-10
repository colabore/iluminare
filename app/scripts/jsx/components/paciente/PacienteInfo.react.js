var React = require('react');
var PacienteInfoStore = require('../../stores/PacienteInfoStore');

var PacienteInfo = React.createClass({
  getInitialState: function() {
   return PacienteInfoStore.get();
  },
  componentDidMount: function() {
    PacienteInfoStore.addChangeListener(this._onData);
  },
  componentWillUnmount: function() {
    PacienteInfoStore.removeChangeListener(this._onData);
  },
  _onData: function() {
    this.setState(PacienteInfoStore.get());
  },
  render: function() {
    return (
      <ul></ul>
    )
  }
});

module.exports = PacienteInfo;
