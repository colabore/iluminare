var React = require('react');
var MaterialUI = require('material-ui'),
  Tabs = MaterialUI.Tabs,
  Tab = MaterialUI.Tab,
  List = MaterialUI.List,
  ListItem = MaterialUI.ListItem,
  TextField = MaterialUI.TextField;

var model;
var subscription;

var PacienteDetails = React.createClass({
  getInitialState: function() {
    return {
      'nome': 'Nome do paciente'
    }
  },
  componentDidMount: function() {
    model.infoAction.onNext(this.props.params.id);
    subscription = model.infoStore.subscribe(this.setState.bind(this));
  },
  componentWillUnmount: function() {
    subscription.dispose();
  },
  render: function() {
    return (
      <div>
        <h2 className="paper-font-display2">Paciente</h2>
        <Tabs>
          <Tab label="Informações">
            <List>
              <ListItem>Nome: {this.state.nome}</ListItem>
            </List>
          </Tab>
          <Tab label="Tratamentos">
            <p>Informação não disponível</p>
          </Tab>
          <Tab label="Atendimentos">
            <p>Informação não disponível</p>
          </Tab>
        </Tabs>
      </div>
    )
  }
});


function create(options) {
  if (!options.infoStore)
    throw new Error('infoStore is required');

  if (!options.infoAction)
    throw new Error('infoAction is required');

  model = options;
  return PacienteDetails;
}
module.exports = create;
