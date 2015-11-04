var React = require('react');
var MaterialUI = require('material-ui');
var TratamentoList = require('../tratamento/TratamentoList.react');

var model;

var Tratamento = React.createClass({
  render: function () {
    return (
      <div>
        <TratamentoList tratamentos={model.tratamentos} />
      </div>
    )
  }
});

function create(options) {
  if (!options.tratamentos)
    throw new Error('tratamentos is required');

  model = options;
  return Tratamento;
}

module.exports = create;
